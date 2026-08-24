"""Сервис заданий."""

from __future__ import annotations

import logging

from app.warehouse.models import Task, TaskLine
from app.warehouse.repository import TaskLineRepository, TaskRepository
from app.warehouse.services.stock_service import StockService
from app.infrastructure.events import event_bus
from app.infrastructure.events.event_types import EventTypes

logger = logging.getLogger(__name__)


class TaskService:
    def __init__(
        self,
        task_repo: TaskRepository,
        line_repo: TaskLineRepository,
        stock_service: StockService,
    ) -> None:
        self._tasks = task_repo
        self._lines = line_repo
        self._stock = stock_service

    async def get_by_id(self, task_id: int) -> Task | None:
        return await self._tasks.get_by_id(task_id)

    async def list_all(self) -> list[Task]:
        return await self._tasks.list_all()

    async def create(self, *, user_id: int | None = None, task_type: str, document_id: int | None = None, assignee_id: int | None = None) -> Task:
        return await self._tasks.create(
            task_type=task_type,
            document_id=document_id,
            assignee_id=assignee_id,
        )

    async def update(self, task_id: int, user_id: int | None = None, **kwargs) -> Task | None:
        return await self._tasks.update(task_id, **kwargs)

    async def soft_delete(self, task_id: int, user_id: int | None = None) -> bool:
        return await self._tasks.soft_delete(task_id, user_id)

    async def get_line(self, line_id: int) -> TaskLine | None:
        return await self._lines.get_by_id(line_id)

    async def list_lines(self, task_id: int) -> list[TaskLine]:
        return await self._lines.list_by_task(task_id)

    async def add_line(self, *, user_id: int, task_id: int, product_id: int, plan_qty: int = 0, **kwargs) -> TaskLine:
        return await self._lines.create(
            task_id=task_id,
            product_id=product_id,
            plan_qty=plan_qty,
            **kwargs,
        )

    async def update_line(self, line_id: int, user_id: int | None = None, **kwargs) -> TaskLine | None:
        return await self._lines.update(line_id, **kwargs)

    async def delete_line(self, line_id: int, user_id: int | None = None) -> bool:
        return await self._lines.soft_delete(line_id, user_id)

    async def start(self, *, user_id: int, task_id: int) -> Task | None:
        return await self._tasks.update(task_id, status="in_progress")

    async def complete_line(
        self, *, user_id: int, task_line_id: int, fact_qty: int, **kwargs
    ) -> TaskLine:
        if fact_qty <= 0:
            raise ValueError("Количество должно быть больше 0")

        line = await self._lines.get_by_id(task_line_id)
        if line is None:
            raise ValueError("Строка задания не найдена")

        task = await self._tasks.get_by_id(line.task_id)
        if task.status == "new":
            await self._tasks.update(task.id, status="in_progress")

        if task.task_type in ["receiving", "putaway"]:
            await self._stock.add_stock(
                user_id=user_id,
                product_id=line.product_id,
                location_id=kwargs.get("location_id") or line.to_location_id,
                quantity=fact_qty,
                lpn_id=line.lpn_id,
                batch_id=kwargs.get("batch_id") or line.batch_id,
                document_id=task.document_id,
            )
        elif task.task_type in ["picking", "shipping"]:
            await self._stock.remove_stock(
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

    async def complete(self, *, user_id: int, task_id: int, force: bool = False) -> Task:
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

    async def cancel(self, *, user_id: int, task_id: int) -> Task | None:
        task = await self._tasks.get_by_id(task_id)
        if task is None:
            raise ValueError("Задание не найдено")
        if task.status == "completed":
            raise ValueError("Нельзя отменить завершённое задание")
        return await self._tasks.update(task_id, status="cancelled")
