"""Приёмка: inbound → задание → факт → остаток."""

from __future__ import annotations

from datetime import timedelta
from decimal import Decimal

from app.core.exceptions import BadRequestError, NotFoundError
from app.core.statuses import OrderStatus, TaskStatus
from app.infrastructure.events import schedule_event
from app.infrastructure.events.event_types import EventTypes
from app.orders.repository import InboundOrderLineRepository, InboundOrderRepository
from app.warehouse.models import Task, TaskLine
from app.warehouse.repository import (
    LocationRepository,
    ProductRepository,
    ReceivingDiscrepancyRepository,
    StockRepository,
    TaskLineRepository,
    TaskRepository,
)
from app.warehouse.services.batch_service import BatchService
from app.warehouse.services.lpn_service import LPNService
from app.warehouse.services.placement_service import PlacementService
from app.warehouse.services.plan_fact_view import (
    discrepancy_kind,
    movement_row,
    product_label,
)
from app.warehouse.services.stock_service import StockService


class ReceivingService:
    def __init__(
        self,
        *,
        tasks: TaskRepository,
        lines: TaskLineRepository,
        inbound: InboundOrderRepository,
        inbound_lines: InboundOrderLineRepository,
        stock: StockService,
        stock_repo: StockRepository,
        batches: BatchService,
        lpns: LPNService,
        products: ProductRepository,
        locations: LocationRepository,
        placement: PlacementService,
        discrepancies: ReceivingDiscrepancyRepository,
    ) -> None:
        self._tasks = tasks
        self._lines = lines
        self._inbound = inbound
        self._inbound_lines = inbound_lines
        self._stock = stock
        self._stock_repo = stock_repo
        self._batches = batches
        self._lpns = lpns
        self._products = products
        self._locations = locations
        self._placement = placement
        self._discrepancies = discrepancies

    async def create_from_inbound(
        self,
        *,
        user_id: int | None,
        inbound_order_id: int,
        receiving_location_id: int | None = None,
    ) -> Task:
        order = await self._inbound.get_by_id(inbound_order_id)
        if order is None:
            raise NotFoundError("Входящий заказ не найден")
        if not order.warehouse_id:
            raise BadRequestError("У заказа нет склада")

        existing = await self._tasks.get_active_for_inbound(inbound_order_id)
        if existing is not None:
            if existing.status in (
                TaskStatus.COMPLETED.value,
                TaskStatus.COMPLETED_WITH_DEVIATIONS.value,
            ):
                raise BadRequestError("Приёмка по заказу уже завершена")
            return existing

        location_id = receiving_location_id
        if location_id is None:
            raise BadRequestError("Укажите ячейку приёмки")
        if not await self._locations.belongs_to_warehouse(location_id, order.warehouse_id):
            raise BadRequestError("Ячейка не принадлежит складу заказа")

        task = await self._tasks.create(
            task_type="receiving",
            inbound_order_id=order.id,
            status=TaskStatus.NEW.value,
            created_by_id=user_id,
        )
        for ol in await self._inbound_lines.list_by_order(order.id):
            if not ol.product_id:
                raise BadRequestError("В строке заказа нет товара")
            await self._lines.create(
                task_id=task.id,
                product_id=ol.product_id,
                inbound_order_line_id=ol.id,
                plan_qty=ol.quantity,
                fact_qty=Decimal("0"),
                to_location_id=location_id,
            )
        await self._inbound.update(order.id, status=OrderStatus.TASK_CREATED.value)
        return task

    async def receive_line(
        self,
        *,
        user_id: int | None,
        task_line_id: int,
        quantity: Decimal,
        batch_number: str,
        location_id: int | None = None,
        lpn_id: int | None = None,
        manufacture_date=None,
    ) -> TaskLine:
        if quantity <= 0:
            raise BadRequestError("Количество должно быть больше 0")
        if not batch_number:
            raise BadRequestError("Укажите партию")

        line = await self._lines.get_by_id(task_line_id)
        if line is None:
            raise NotFoundError("Строка задания не найдена")
        task = await self._tasks.get_by_id(line.task_id)
        if task is None or task.task_type != "receiving":
            raise BadRequestError("Это не строка приёмки")
        if task.status in (
            TaskStatus.COMPLETED.value,
            TaskStatus.COMPLETED_WITH_DEVIATIONS.value,
            TaskStatus.CANCELLED.value,
        ):
            raise BadRequestError("Задание уже закрыто")
        if line.fact_qty + quantity > line.plan_qty:
            raise BadRequestError("Факт не может быть больше плана")

        product = await self._products.get_by_id(line.product_id)
        exp = None
        if manufacture_date and product and product.shelf_life_days:
            exp = manufacture_date + timedelta(days=product.shelf_life_days)
        batch, _ = await self._batches.get_or_create(
            product_id=line.product_id,
            batch_number=batch_number,
            user_id=user_id,
            production_date=manufacture_date,
            expiration_date=exp,
        )
        if line.batch_id and line.batch_id != batch.id:
            raise BadRequestError("В строке уже есть другая партия")

        order = (
            await self._inbound.get_by_id(task.inbound_order_id)
            if task.inbound_order_id
            else None
        )
        dest_id = location_id or line.to_location_id
        if dest_id is None and order and order.warehouse_id:
            _kind, loc, _old = await self._placement.find_location(
                product_id=line.product_id,
                batch_id=batch.id,
                warehouse_id=order.warehouse_id,
            )
            dest_id = loc.id if loc else None
        if dest_id is None:
            raise BadRequestError("Укажите ячейку приёмки")
        if order and order.warehouse_id:
            if not await self._locations.belongs_to_warehouse(dest_id, order.warehouse_id):
                raise BadRequestError("Ячейка не принадлежит складу заказа")

        if lpn_id is None:
            lpn = await self._lpns.create(user_id=user_id, status="assigned")
            lpn_id = lpn.id

        document_id = task.document_id

        await self._stock.add_stock(
            user_id=user_id,
            product_id=line.product_id,
            location_id=dest_id,
            quantity=quantity,
            lpn_id=lpn_id,
            batch_id=batch.id,
            document_id=document_id,
            task_line_id=line.id,
        )
        line.fact_qty += quantity
        line.to_location_id = dest_id
        line.lpn_id = lpn_id
        line.batch_id = batch.id
        line.updated_by_id = user_id
        if task.status == TaskStatus.NEW.value:
            task.status = TaskStatus.IN_PROGRESS.value
        if order and order.status in (OrderStatus.NEW.value, OrderStatus.TASK_CREATED.value, OrderStatus.DOCUMENT_CREATED.value):
            order.status = OrderStatus.IN_PROGRESS.value
        await self._lines._s.flush()
        await self._sync_discrepancy(line)
        return line

    async def complete(self, *, user_id: int | None, task_id: int, confirm_shortage: bool = False) -> Task:
        task = await self._tasks.get_by_id(task_id)
        if task is None or task.task_type != "receiving":
            raise NotFoundError("Задание приёмки не найдено")
        if task.status in (TaskStatus.COMPLETED.value, TaskStatus.COMPLETED_WITH_DEVIATIONS.value):
            return task

        lines = await self._lines.list_by_task(task.id)
        shortage = any(ln.fact_qty < ln.plan_qty for ln in lines)
        if shortage and not confirm_shortage:
            raise BadRequestError("Обнаружен недогруз. Подтвердите закрытие")

        for ln in lines:
            await self._sync_discrepancy(ln)

        status = (
            TaskStatus.COMPLETED_WITH_DEVIATIONS.value
            if shortage
            else TaskStatus.COMPLETED.value
        )
        task.status = status
        task.updated_by_id = user_id
        if task.inbound_order_id:
            await self._inbound.update(
                task.inbound_order_id,
                status=OrderStatus.COMPLETED.value,
                has_shortage=shortage,
            )
            schedule_event(
                self._tasks._s,
                EventTypes.RECEIVING_TASK_COMPLETED,
                {
                    "task_id": task.id,
                    "inbound_order_id": task.inbound_order_id,
                    "has_shortage": shortage,
                },
            )
        await self._tasks._s.flush()
        return task

    async def cancel_movement(self, *, user_id: int | None, movement_id: int) -> None:
        movement = await self._stock_repo.get_movement(movement_id)
        if movement is None:
            raise NotFoundError("Движение не найдено")
        if movement.direction != "in" or not movement.task_line_id:
            raise BadRequestError("Можно откатить только приход по строке задания")
        line = await self._lines.get_by_id(movement.task_line_id)
        if line is None:
            raise NotFoundError("Строка задания не найдена")
        task = await self._tasks.get_by_id(line.task_id)
        if task is None:
            raise NotFoundError("Задание не найдено")
        if task.status in (
            TaskStatus.COMPLETED.value,
            TaskStatus.COMPLETED_WITH_DEVIATIONS.value,
        ):
            raise BadRequestError("Нельзя откатить приёмку из завершённого задания")
        if movement.lpn_id is None:
            raise BadRequestError("У движения нет LPN")

        await self._stock.remove_stock(
            user_id=user_id,
            product_id=movement.product_id,
            location_id=movement.location_id,
            quantity=movement.quantity,
            lpn_id=movement.lpn_id,
            batch_id=movement.batch_id,
            document_id=movement.document_id,
            task_line_id=line.id,
        )
        line.fact_qty -= movement.quantity
        if line.fact_qty < 0:
            line.fact_qty = Decimal("0")
        line.updated_by_id = user_id
        await self._lines._s.flush()
        await self._sync_discrepancy(line)

    async def _sync_discrepancy(self, line: TaskLine) -> None:
        existing = await self._discrepancies.list_by_line(line.id)
        live = next((d for d in existing if not d.is_deleted), None)
        if line.fact_qty == line.plan_qty:
            if live:
                live.qty_planned = line.plan_qty
                live.qty_fact = line.fact_qty
                live.status = "resolved"
            return
        kind = "shortage" if line.fact_qty < line.plan_qty else "surplus"
        if live:
            live.discrepancy_type = kind
            live.qty_planned = line.plan_qty
            live.qty_fact = line.fact_qty
            live.status = "detected"
            return
        await self._discrepancies.create(
            task_line_id=line.id,
            discrepancy_type=kind,
            qty_planned=line.plan_qty,
            qty_fact=line.fact_qty,
            status="detected",
        )

    async def plan_fact_for_inbound(self, inbound_order_id: int) -> dict:
        """План (строки заявки), факт (движения) и сверка для карточки заказа."""
        order = await self._inbound.get_by_id(inbound_order_id)
        if order is None:
            raise NotFoundError("Входящий заказ не найден")

        plan_lines = await self._inbound_lines.list_by_order(order.id)
        task_lines = await self._lines.list_for_inbound(order.id)
        movements = await self._stock_repo.list_movements_for_inbound(order.id)

        plan = [
            {
                "id": line.id,
                "product_id": line.product_id,
                **product_label(line.product),
                "quantity": line.quantity,
                "batch_number": line.batch_number,
                "manufacture_date": line.manufacture_date,
            }
            for line in plan_lines
        ]
        fact = [movement_row(move) for move in movements]

        by_order_line: dict[int, list] = {}
        unmatched: list = []
        for tl in task_lines:
            if tl.inbound_order_line_id:
                by_order_line.setdefault(tl.inbound_order_line_id, []).append(tl)
            else:
                unmatched.append(tl)

        discrepancies: list[dict] = []
        used_task_lines: set[int] = set()
        for line in plan_lines:
            related = by_order_line.get(line.id, [])
            fact_qty = sum((tl.fact_qty for tl in related), Decimal("0"))
            used_task_lines.update(tl.id for tl in related)
            planned = line.quantity
            discrepancies.append(
                {
                    "inbound_order_line_id": line.id,
                    "product_id": line.product_id,
                    **product_label(line.product),
                    "qty_planned": planned,
                    "qty_fact": fact_qty,
                    "qty_diff": fact_qty - planned,
                    "kind": discrepancy_kind(planned, fact_qty),
                }
            )

        for tl in unmatched:
            if tl.id in used_task_lines:
                continue
            discrepancies.append(
                {
                    "inbound_order_line_id": None,
                    "product_id": tl.product_id,
                    **product_label(tl.product),
                    "qty_planned": Decimal("0"),
                    "qty_fact": tl.fact_qty,
                    "qty_diff": tl.fact_qty,
                    "kind": "surplus" if tl.fact_qty else "match",
                }
            )

        return {"plan": plan, "fact": fact, "discrepancies": discrepancies}
