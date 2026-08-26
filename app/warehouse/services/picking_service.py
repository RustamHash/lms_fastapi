"""Отбор: outbound → FEFO-план → резерв → списание."""

from __future__ import annotations

from collections import defaultdict
from decimal import Decimal

from app.core.exceptions import BadRequestError, NotFoundError
from app.core.statuses import OrderStatus, TaskStatus
from app.infrastructure.events import schedule_event
from app.infrastructure.events.event_types import EventTypes
from app.orders.repository import OutboundOrderLineRepository, OutboundOrderRepository
from app.warehouse.models import Task, TaskLine
from app.warehouse.repository import StockRepository, TaskLineRepository, TaskRepository
from app.warehouse.services.plan_fact_view import (
    discrepancy_kind,
    movement_row,
    product_label,
)
from app.warehouse.services.stock_service import StockService


class PickingService:
    def __init__(
        self,
        *,
        tasks: TaskRepository,
        lines: TaskLineRepository,
        outbound: OutboundOrderRepository,
        outbound_lines: OutboundOrderLineRepository,
        stock: StockService,
        stock_repo: StockRepository,
    ) -> None:
        self._tasks = tasks
        self._lines = lines
        self._outbound = outbound
        self._outbound_lines = outbound_lines
        self._stock = stock
        self._stock_repo = stock_repo

    async def create_from_outbound(self, *, user_id: int | None, outbound_order_id: int) -> Task:
        order = await self._outbound.get_by_id(outbound_order_id)
        if order is None:
            raise NotFoundError("Исходящий заказ не найден")
        if order.delivery_only:
            raise BadRequestError("Заказ только на доставку, без склада")
        if not order.warehouse_id:
            raise BadRequestError("У заказа нет склада")

        existing = await self._tasks.get_active_for_outbound(outbound_order_id)
        if existing is not None:
            if existing.status in (
                TaskStatus.COMPLETED.value,
                TaskStatus.COMPLETED_WITH_DEVIATIONS.value,
            ):
                raise BadRequestError("Отбор по заказу уже завершён")
            return existing

        task = await self._tasks.create(
            task_type="picking",
            outbound_order_id=order.id,
            status=TaskStatus.NEW.value,
            created_by_id=user_id,
        )
        await self._outbound.update(order.id, status=OrderStatus.TASK_CREATED.value)
        return task

    async def plan_lines(self, *, user_id: int | None, task_id: int) -> Task:
        task = await self._tasks.get_by_id(task_id)
        if task is None or task.task_type != "picking":
            raise NotFoundError("Задание отбора не найдено")
        if not task.outbound_order_id:
            raise BadRequestError("У задания нет исходящего заказа")
        order = await self._outbound.get_by_id(task.outbound_order_id)
        if order is None or not order.warehouse_id:
            raise BadRequestError("У заказа нет склада")

        existing = await self._lines.list_by_task(task.id)
        if any(ln.fact_qty > 0 for ln in existing):
            raise BadRequestError("Нельзя перепланировать: уже есть факт")
        for ln in existing:
            await self._release_line(user_id, ln)
            await self._lines.soft_delete(ln.id, user_id)

        need: dict[int, Decimal] = defaultdict(lambda: Decimal("0"))
        for ol in await self._outbound_lines.list_by_order(order.id):
            if not ol.product_id:
                raise BadRequestError("В строке заказа нет товара")
            need[ol.product_id] += ol.quantity

        for product_id, qty in need.items():
            remaining = qty
            balances = await self._stock_repo.list_available_fefo(product_id, order.warehouse_id)
            for balance in balances:
                available = balance.quantity - balance.reserved_quantity
                if available <= 0:
                    continue
                take = min(available, remaining)
                await self._stock.reserve(
                    user_id=user_id,
                    product_id=product_id,
                    location_id=balance.location_id,
                    quantity=take,
                    lpn_id=balance.lpn_id,
                    batch_id=balance.batch_id,
                )
                await self._lines.create(
                    task_id=task.id,
                    product_id=product_id,
                    plan_qty=take,
                    fact_qty=Decimal("0"),
                    from_location_id=balance.location_id,
                    lpn_id=balance.lpn_id,
                    batch_id=balance.batch_id,
                    reserved=True,
                )
                remaining -= take
                if remaining <= 0:
                    break
            if remaining > 0:
                await self._lines.create(
                    task_id=task.id,
                    product_id=product_id,
                    plan_qty=remaining,
                    fact_qty=Decimal("0"),
                    reserved=False,
                )

        task.status = TaskStatus.IN_PROGRESS.value
        task.updated_by_id = user_id
        if order.status in (OrderStatus.NEW.value, OrderStatus.TASK_CREATED.value, OrderStatus.DOCUMENT_CREATED.value):
            order.status = OrderStatus.IN_PROGRESS.value
        await self._tasks._s.flush()
        return task

    async def pick_line(self, *, user_id: int | None, task_line_id: int, quantity: Decimal) -> TaskLine:
        if quantity <= 0:
            raise BadRequestError("Количество должно быть больше 0")
        line = await self._lines.get_by_id(task_line_id)
        if line is None:
            raise NotFoundError("Строка задания не найдена")
        task = await self._tasks.get_by_id(line.task_id)
        if task is None or task.task_type != "picking":
            raise BadRequestError("Это не строка отбора")
        if task.status in (
            TaskStatus.COMPLETED.value,
            TaskStatus.COMPLETED_WITH_DEVIATIONS.value,
            TaskStatus.CANCELLED.value,
        ):
            raise BadRequestError("Задание уже закрыто")
        if not line.from_location_id or not line.lpn_id or not line.batch_id:
            raise BadRequestError("Нет остатка для этой строки (дефицит FEFO)")
        if line.fact_qty + quantity > line.plan_qty:
            raise BadRequestError("Факт не может быть больше плана")

        if line.reserved:
            await self._stock.unreserve(
                user_id=user_id,
                product_id=line.product_id,
                location_id=line.from_location_id,
                quantity=quantity,
                lpn_id=line.lpn_id,
                batch_id=line.batch_id,
            )
        await self._stock.remove_stock(
            user_id=user_id,
            product_id=line.product_id,
            location_id=line.from_location_id,
            quantity=quantity,
            lpn_id=line.lpn_id,
            batch_id=line.batch_id,
            document_id=task.document_id,
            task_line_id=line.id,
        )
        line.fact_qty += quantity
        if line.fact_qty >= line.plan_qty:
            line.reserved = False
        line.updated_by_id = user_id
        await self._lines._s.flush()
        return line

    async def complete(self, *, user_id: int | None, task_id: int) -> Task:
        task = await self._tasks.get_by_id(task_id)
        if task is None or task.task_type != "picking":
            raise NotFoundError("Задание отбора не найдено")
        lines = await self._lines.list_by_task(task.id)
        unfinished = [ln for ln in lines if ln.from_location_id and ln.fact_qty < ln.plan_qty]
        if unfinished:
            raise BadRequestError("Есть не отобранные строки")
        shortfall = any(ln.from_location_id is None and ln.plan_qty > 0 for ln in lines)
        status = (
            TaskStatus.COMPLETED_WITH_DEVIATIONS.value
            if shortfall
            else TaskStatus.COMPLETED.value
        )
        task.status = status
        task.updated_by_id = user_id
        if task.outbound_order_id:
            await self._outbound.update(
                task.outbound_order_id,
                status=OrderStatus.COMPLETED.value,
            )
            schedule_event(
                self._tasks._s,
                EventTypes.PICKING_TASK_COMPLETED,
                {
                    "task_id": task.id,
                    "outbound_order_id": task.outbound_order_id,
                    "has_shortfall": shortfall,
                },
            )
        await self._tasks._s.flush()
        return task

    async def _release_line(self, user_id: int | None, line: TaskLine) -> None:
        leftover = line.plan_qty - line.fact_qty
        if not line.reserved or leftover <= 0:
            return
        if not line.from_location_id or not line.lpn_id or not line.batch_id:
            return
        await self._stock.unreserve(
            user_id=user_id,
            product_id=line.product_id,
            location_id=line.from_location_id,
            quantity=leftover,
            lpn_id=line.lpn_id,
            batch_id=line.batch_id,
        )
        line.reserved = False

    async def plan_fact_for_outbound(self, outbound_order_id: int) -> dict:
        """План (строки заявки), факт (движения) и сверка для карточки заказа."""
        order = await self._outbound.get_by_id(outbound_order_id)
        if order is None:
            raise NotFoundError("Исходящий заказ не найден")

        plan_lines = await self._outbound_lines.list_by_order(order.id)
        task_lines = await self._lines.list_for_outbound(order.id)
        movements = await self._stock_repo.list_movements_for_outbound(order.id)

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

        planned_by_product: dict[int, Decimal] = defaultdict(lambda: Decimal("0"))
        labels: dict[int, dict[str, str]] = {}
        for line in plan_lines:
            if not line.product_id:
                continue
            planned_by_product[line.product_id] += line.quantity
            labels[line.product_id] = product_label(line.product)

        fact_by_product: dict[int, Decimal] = defaultdict(lambda: Decimal("0"))
        for tl in task_lines:
            fact_by_product[tl.product_id] += tl.fact_qty
            labels.setdefault(tl.product_id, product_label(tl.product))

        product_ids = sorted(set(planned_by_product) | set(fact_by_product))
        discrepancies = []
        for product_id in product_ids:
            planned = planned_by_product[product_id]
            fact_qty = fact_by_product[product_id]
            discrepancies.append(
                {
                    "inbound_order_line_id": None,
                    "product_id": product_id,
                    **labels.get(product_id, product_label(None)),
                    "qty_planned": planned,
                    "qty_fact": fact_qty,
                    "qty_diff": fact_qty - planned,
                    "kind": discrepancy_kind(planned, fact_qty),
                }
            )

        return {"plan": plan, "fact": fact, "discrepancies": discrepancies}
