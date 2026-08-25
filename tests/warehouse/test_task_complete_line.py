from decimal import Decimal

import pytest

from app.core.exceptions import BadRequestError
from app.warehouse.models import Task, TaskLine
from app.warehouse.repository import StockRepository, TaskLineRepository, TaskRepository
from app.warehouse.services.stock_service import StockService
from app.warehouse.services.task_service import TaskService


async def test_complete_line_requires_lpn(session, stock_ctx) -> None:
    tasks = TaskRepository(session)
    lines = TaskLineRepository(session)
    stock = StockService(StockRepository(session))
    svc = TaskService(tasks, lines, stock)

    task = await tasks.create(task_type="receiving")
    line = await lines.create(
        task_id=task.id,
        product_id=stock_ctx["product_id"],
        plan_qty=1,
        to_location_id=stock_ctx["location_id"],
        batch_id=stock_ctx["batch_id"],
        lpn_id=None,
    )
    with pytest.raises(BadRequestError, match="LPN"):
        await svc.complete_line(user_id=stock_ctx["user_id"], task_line_id=line.id, fact_qty=1)


async def test_complete_line_writes_task_line_id(session, stock_ctx) -> None:
    tasks = TaskRepository(session)
    lines = TaskLineRepository(session)
    stock = StockService(StockRepository(session))
    svc = TaskService(tasks, lines, stock)

    task = await tasks.create(task_type="receiving")
    line = await lines.create(
        task_id=task.id,
        product_id=stock_ctx["product_id"],
        plan_qty=2,
        to_location_id=stock_ctx["location_id"],
        batch_id=stock_ctx["batch_id"],
        lpn_id=stock_ctx["lpn_id"],
    )
    await svc.complete_line(user_id=stock_ctx["user_id"], task_line_id=line.id, fact_qty=2)
    movements = await StockRepository(session).list_movements(product_id=stock_ctx["product_id"])
    assert len(movements) == 1
    assert movements[0].task_line_id == line.id
    assert movements[0].quantity == Decimal("2")
