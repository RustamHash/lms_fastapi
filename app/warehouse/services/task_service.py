"""Сервис заданий."""

from __future__ import annotations

import logging

from app.warehouse.repository import TaskLineRepository, TaskRepository
from app.warehouse.services.stock_service import StockService
from app.infrastructure.events import event_bus
from app.infrastructure.events.event_types import EventTypes
from app.documents.services.document_service import DocumentService
from app.documents.repository import DocumentLineRepository, DocumentRepository
from app.documents.document_types import DocumentType

logger = logging.getLogger(__name__)


class TaskService:
    def __init__(self, task_repo: TaskRepository, line_repo: TaskLineRepository, stock_service: StockService) -> None:
        self._tasks = task_repo
        self._lines = line_repo
        self.stock = stock_service

    async def create(self, *, user_id: int, task_type: str, document_id: int | None = None, assignee_id: int | None = None):
        logger.info("Создание задания: type=%s", task_type)
        return await self._tasks.create(
            task_type=task_type,
            document_id=document_id,
            assignee_id=assignee_id,
        )

    async def create_from_document(
        self,
        *,
        user_id: int,
        document_id: int,
        task_type: str,
        assignee_id: int | None = None,
        warehouse_id: int,
    ):
        """Создать задание на основании документа (все строки)."""
        from app.documents.repository import DocumentLineRepository, DocumentRepository

        doc_repo = DocumentRepository(self._s)
        line_repo = DocumentLineRepository(self._s)

        # Получить документ
        document = await doc_repo.get_by_id(document_id)
        if document is None:
            raise ValueError("Документ не найден")

        # Получить строки документа
        doc_lines = await line_repo.list_by_document(document_id)
        if not doc_lines:
            raise ValueError("Документ не содержит строк")

        # Начало транзакции
        savepoint = await self._s.begin_nested()

        try:
            # Создать задание
            task = await self._tasks.create(
                task_type=task_type,
                document_id=document_id,
                assignee_id=assignee_id,
                warehouse_id=warehouse_id,
                status="new",
                created_by_id=user_id,
                updated_by_id=user_id,
            )

            # Создать строки задания из строк документа
            for doc_line in doc_lines:
                await self._lines.create(
                    task_id=task.id,
                    product_id=doc_line.product_id,
                    document_line_id=doc_line.id,
                    plan_qty=int(doc_line.quantity),
                    fact_qty=0,
                    created_by_id=user_id,
                    updated_by_id=user_id,
                )

            # Обновить статус документа
            document.status = "task_created"
            await self._s.flush()

            return task

        except Exception:
            await savepoint.rollback()
            raise

    async def create_picking_with_fefo(
        self,
        *,
        user_id: int,
        document_id: int,
        assignee_id: int | None = None,
        warehouse_id: int,
    ) -> dict:
        """Создать задание на отбор с проверкой остатков и FEFO."""
        from app.documents.repository import DocumentLineRepository, DocumentRepository
        from app.warehouse.models import StockBalance, ProductLocation, Location, Batch, Zone

        doc_repo = DocumentRepository(self._s)
        line_repo = DocumentLineRepository(self._s)

        document = await doc_repo.get_by_id(document_id)
        if document is None:
            raise ValueError("Документ не найден")

        doc_lines = await line_repo.list_by_document(document_id)
        if not doc_lines:
            raise ValueError("Документ не содержит строк")

        savepoint = await self._s.begin_nested()

        try:
            # Создать основное задание на отбор
            picking_task = await self._tasks.create(
                task_type="picking",
                document_id=document_id,
                assignee_id=assignee_id,
                warehouse_id=warehouse_id,
                status="new",
                created_by_id=user_id,
                updated_by_id=user_id,
            )

            need_replenishment = False

            for doc_line in doc_lines:
                product_id = doc_line.product_id
                required_qty = int(doc_line.quantity)

                # Проверить остатки в зоне отбора
                available = await self._get_available_in_picking_zone(product_id, warehouse_id)

                if available >= required_qty:
                    # Хватает — резервируем
                    await self._reserve_picking_zone(user_id, product_id, required_qty, warehouse_id)

                    # Создать строку задания на отбор
                    await self._lines.create(
                        task_id=picking_task.id,
                        product_id=product_id,
                        document_line_id=doc_line.id,
                        plan_qty=required_qty,
                        fact_qty=0,
                        created_by_id=user_id,
                        updated_by_id=user_id,
                    )
                else:
                    # Не хватает — нужен пополнение
                    need_replenishment = True

            # Если нужно пополнение — создать задание на перемещение
            replenishment_task = None
            if need_replenishment:
                replenishment_task = await self._tasks.create(
                    task_type="movement",
                    document_id=document_id,
                    assignee_id=None,
                    warehouse_id=warehouse_id,
                    status="new",
                    created_by_id=user_id,
                    updated_by_id=user_id,
                )

                # Строки для пополнения из зоны хранения в зону отбора
                for doc_line in doc_lines:
                    product_id = doc_line.product_id
                    required_qty = int(doc_line.quantity)
                    available = await self._get_available_in_picking_zone(product_id, warehouse_id)

                    if available < required_qty:
                        shortage = required_qty - available

                        # Найти ячейку хранения с нужным товаром (FEFO)
                        storage_location = await self._find_storage_location_fefo(product_id, warehouse_id)

                        if storage_location:
                            await self._lines.create(
                                task_id=replenishment_task.id,
                                product_id=product_id,
                                document_line_id=doc_line.id,
                                plan_qty=shortage,
                                fact_qty=0,
                                from_location_id=storage_location.id,
                                to_location_id=None,  # Ячейка отбора — определяется при выполнении
                                created_by_id=user_id,
                                updated_by_id=user_id,
                            )

            # Обновить статус документа
            document.status = "task_created"
            await self._s.flush()

            return {
                "picking_task_id": picking_task.id,
                "replenishment_task_id": replenishment_task.id if replenishment_task else None,
            }

        except Exception:
            await savepoint.rollback()
            raise

    async def _get_available_in_picking_zone(self, product_id: int, warehouse_id: int) -> int:
        """Получить доступное количество товара в зоне отбора."""
        from sqlalchemy import select as sa_select
        from app.warehouse.models import StockBalance, Location, Row, Zone

        stmt = (
            sa_select(StockBalance)
            .join(Location, StockBalance.location_id == Location.id)
            .join(Row, Location.row_id == Row.id)
            .join(Zone, Row.zone_id == Zone.id)
            .where(
                StockBalance.product_id == product_id,
                Zone.warehouse_id == warehouse_id,
                Zone.zone_type == "picking",
            )
        )
        balances = list(await self._s.scalars(stmt))

        total = 0
        for balance in balances:
            total += int(balance.quantity - balance.reserved_quantity)
        return total

    async def _reserve_picking_zone(
        self, user_id: int, product_id: int, quantity: int, warehouse_id: int
    ) -> None:
        """Резервировать товар в зоне отбора."""
        from sqlalchemy import select as sa_select
        from app.warehouse.models import StockBalance, Location, Row, Zone

        stmt = (
            sa_select(StockBalance)
            .join(Location, StockBalance.location_id == Location.id)
            .join(Row, Location.row_id == Row.id)
            .join(Zone, Row.zone_id == Zone.id)
            .where(
                StockBalance.product_id == product_id,
                Zone.warehouse_id == warehouse_id,
                Zone.zone_type == "picking",
            )
            .order_by(StockBalance.id)
        )
        balances = list(await self._s.scalars(stmt))

        remaining = quantity
        for balance in balances:
            available = int(balance.quantity - balance.reserved_quantity)
            if available <= 0:
                continue

            to_reserve = min(remaining, available)
            balance.reserved_quantity += to_reserve
            balance.updated_by_id = user_id
            remaining -= to_reserve

            if remaining <= 0:
                break

        await self._s.flush()

    async def _find_storage_location_fefo(self, product_id: int, warehouse_id: int):
        """Найти ячейку хранения с товаром по FEFO."""
        from sqlalchemy import select as sa_select
        from app.warehouse.models import StockBalance, Location, Row, Zone, Batch

        stmt = (
            sa_select(StockBalance, Location, Batch)
            .join(Location, StockBalance.location_id == Location.id)
            .join(Row, Location.row_id == Row.id)
            .join(Zone, Row.zone_id == Zone.id)
            .join(Batch, StockBalance.batch_id == Batch.id)
            .where(
                StockBalance.product_id == product_id,
                Zone.warehouse_id == warehouse_id,
                Zone.zone_type == "storage",
                StockBalance.quantity > 0,
            )
            .order_by(Batch.expiration_date.asc().nulls_last())
            .limit(1)
        )
        result = await self._s.execute(stmt)
        row = result.first()
        if row:
            return row[1]  # Location
        return None

    async def add_line(self, *, user_id: int, task_id: int, product_id: int, plan_qty: int = 0, **kwargs):
        return await self._lines.create(
            task_id=task_id,
            product_id=product_id,
            plan_qty=plan_qty,
            **kwargs,
        )

    async def start(self, *, user_id: int, task_id: int):
        return await self._tasks.update(task_id, status="in_progress")

    async def complete_line(self, *, user_id: int, task_line_id: int, fact_qty: int, **kwargs):
        if fact_qty <= 0:
            raise ValueError("Количество должно быть больше 0")

        line = await self._lines.get_by_id(task_line_id)
        if line is None:
            raise ValueError("Строка задания не найдена")

        task = await self._tasks.get_by_id(line.task_id)

        if task.status == "new":
            await self._tasks.update(task.id, status="in_progress")

        # Движения
        if task.task_type in ["receiving", "putaway"]:
            await self.stock.add_stock(
                user_id=user_id,
                product_id=line.product_id,
                location_id=kwargs.get("location_id") or line.to_location_id,
                quantity=fact_qty,
                lpn_id=line.lpn_id,
                batch_id=kwargs.get("batch_id") or line.batch_id,
                document_id=task.document_id,
            )
        elif task.task_type in ["picking", "shipping"]:
            await self.stock.remove_stock(
                user_id=user_id,
                product_id=line.product_id,
                location_id=kwargs.get("location_id") or line.from_location_id,
                quantity=fact_qty,
                lpn_id=line.lpn_id,
                batch_id=kwargs.get("batch_id") or line.batch_id,
                document_id=task.document_id,
            )

        line.fact_qty += fact_qty
        if not line.batch_id and kwargs.get("batch_id"):
            line.batch_id = kwargs["batch_id"]
        line.updated_by_id = user_id
        await self._lines._s.flush()

        return line

    async def complete(self, *, user_id: int, task_id: int, force: bool = False):
        task = await self._tasks.get_by_id(task_id)
        if task is None:
            raise ValueError("Задание не найдено")

        lines = await self._lines.list_by_task(task_id)

        has_deviation = any(line.fact_qty != line.plan_qty for line in lines)
        has_unfinished = any(line.plan_qty > 0 and line.fact_qty < line.plan_qty for line in lines)

        if (has_deviation or has_unfinished) and not force:
            raise ValueError("Есть отклонения. Завершите с force=True")

        status = "completed_with_deviations" if (has_deviation or has_unfinished) else "completed"
        task = await self._tasks.update(task_id, status=status)

        await event_bus.emit(EventTypes.TASK_COMPLETED, {
            "_event_type": EventTypes.TASK_COMPLETED,
            "task_id": task.id,
            "task_type": task.task_type,
        })

        return task

    async def cancel(self, *, user_id: int, task_id: int):
        task = await self._tasks.get_by_id(task_id)
        if task is None:
            raise ValueError("Задание не найдено")
        if task.status == "completed":
            raise ValueError("Нельзя отменить завершённое задание")
        return await self._tasks.update(task_id, status="cancelled")
