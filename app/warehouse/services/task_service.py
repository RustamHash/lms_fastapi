"""Сервис заданий."""

from __future__ import annotations

import logging

from sqlalchemy import select

logger = logging.getLogger(__name__)
from sqlalchemy.ext.asyncio import AsyncSession

from app.warehouse.models import Task, TaskLine
from app.infrastructure.events import event_bus
from app.infrastructure.events.event_types import EventTypes
from app.warehouse.services.stock_service import StockService


class TaskService:
    def __init__(self, session: AsyncSession) -> None:
        self._s = session
        self.stock = StockService(session)

    async def create(
        self,
        *,
        user_id: int,
        task_type: str,
        document_id: int | None = None,
        assignee_id: int | None = None,
    ) -> Task:
        logger.info("Создание задания: type=%s", task_type)
        task = Task(
            task_type=task_type,
            document_id=document_id,
            assignee_id=assignee_id,
            created_by_id=user_id,
            updated_by_id=user_id,
        )
        self._s.add(task)
        await self._s.flush()
        return task

    async def add_line(
        self,
        *,
        user_id: int,
        task_id: int,
        product_id: int,
        plan_qty: int = 0,
        from_location_id: int | None = None,
        to_location_id: int | None = None,
        lpn_id: int | None = None,
        batch_id: int | None = None,
        document_line_id: int | None = None,
    ) -> TaskLine:
        line = TaskLine(
            task_id=task_id,
            product_id=product_id,
            plan_qty=plan_qty,
            from_location_id=from_location_id,
            to_location_id=to_location_id,
            lpn_id=lpn_id,
            batch_id=batch_id,
            document_line_id=document_line_id,
            created_by_id=user_id,
            updated_by_id=user_id,
        )
        self._s.add(line)
        await self._s.flush()
        return line

    async def start(self, *, user_id: int, task_id: int) -> Task | None:
        task = await self._s.get(Task, task_id)
        if task is None:
            return None
        task.status = "in_progress"
        task.updated_by_id = user_id
        await self._s.flush()
        return task

    async def complete_line(
        self,
        *,
        user_id: int,
        task_line_id: int,
        fact_qty: int,
        location_id: int | None = None,
        to_location_id: int | None = None,
        batch_id: int | None = None,
    ) -> TaskLine:
        if fact_qty <= 0:
            raise ValueError("Количество должно быть больше 0")

        line = await self._s.get(TaskLine, task_line_id)
        if line is None:
            raise ValueError("Строка задания не найдена")

        task = await self._s.get(Task, line.task_id)

        # Автостарт задания
        if task.status == "new":
            task.status = "in_progress"
            task.updated_by_id = user_id

        # Фиксируем движение
        if task.task_type in ["receiving", "putaway"]:
            await self.stock.add_stock(
                user_id=user_id,
                product_id=line.product_id,
                location_id=location_id or line.to_location_id,
                quantity=fact_qty,
                lpn_id=line.lpn_id,
                batch_id=batch_id or line.batch_id,
                document_id=task.document_id,
            )
        elif task.task_type in ["picking", "shipping"]:
            await self.stock.remove_stock(
                user_id=user_id,
                product_id=line.product_id,
                location_id=location_id or line.from_location_id,
                quantity=fact_qty,
                lpn_id=line.lpn_id,
                batch_id=batch_id or line.batch_id,
                document_id=task.document_id,
            )
        elif task.task_type == "movement":
            await self.stock.move_stock(
                user_id=user_id,
                product_id=line.product_id,
                from_location_id=location_id or line.from_location_id,
                to_location_id=to_location_id or line.to_location_id,
                quantity=fact_qty,
                lpn_id=line.lpn_id,
                batch_id=batch_id or line.batch_id,
                document_id=task.document_id,
            )

        logger.info("Выполнение строки задания: line=%s, fact=%s", task_line_id, fact_qty)
        # Накапливаем факт
        line.fact_qty += fact_qty
        if not line.batch_id and batch_id:
            line.batch_id = batch_id
        line.updated_by_id = user_id
        await self._s.flush()

        return line

    async def complete(self, *, user_id: int, task_id: int, force: bool = False) -> Task:
        task = await self._s.get(Task, task_id)
        if task is None:
            raise ValueError("Задание не найдено")

        lines = list(await self._s.scalars(
            select(TaskLine).where(TaskLine.task_id == task_id)
        ))

        has_deviation = any(line.fact_qty != line.plan_qty for line in lines)
        has_unfinished = any(
            line.plan_qty > 0 and line.fact_qty < line.plan_qty for line in lines
        )

        if (has_deviation or has_unfinished) and not force:
            raise ValueError("Есть отклонения. Завершите с force=True")

        if has_deviation or has_unfinished:
            task.status = "completed_with_deviations"
        else:
            task.status = "completed"

        task.updated_by_id = user_id
        await self._s.flush()

        # Отправить событие
        await event_bus.emit(EventTypes.TASK_COMPLETED, {
            "_event_type": EventTypes.TASK_COMPLETED,
            "task_id": task.id,
            "task_type": task.task_type,
        })

        return task

    async def cancel(self, *, user_id: int, task_id: int) -> Task:
        task = await self._s.get(Task, task_id)
        if task is None:
            raise ValueError("Задание не найдено")

        if task.status == "completed":
            raise ValueError("Нельзя отменить завершённое задание")

        task.status = "cancelled"
        task.updated_by_id = user_id
        await self._s.flush()
        return task
