"""Outbound → FEFO-план → остаток списан."""

from __future__ import annotations

from datetime import date, timedelta
from decimal import Decimal

from sqlalchemy.ext.asyncio import AsyncSession

from app.orders.models import OutboundOrder, OutboundOrderLine
from app.orders.repository import OutboundOrderLineRepository, OutboundOrderRepository
from app.parties.models.client import Client
from app.warehouse.models import Batch
from app.warehouse.repository import StockRepository, TaskLineRepository, TaskRepository
from app.warehouse.services.picking_service import PickingService
from app.warehouse.services.stock_service import StockService


def _picking(session: AsyncSession) -> PickingService:
    return PickingService(
        tasks=TaskRepository(session),
        lines=TaskLineRepository(session),
        outbound=OutboundOrderRepository(session),
        outbound_lines=OutboundOrderLineRepository(session),
        stock=StockService(StockRepository(session)),
        stock_repo=StockRepository(session),
    )


async def test_outbound_fefo_pick_reduces_stock(session: AsyncSession, stock_ctx: dict) -> None:
    old_batch = await session.get(Batch, stock_ctx["batch_id"])
    assert old_batch is not None
    old_batch.expiration_date = date.today() + timedelta(days=5)

    newer = Batch(
        product_id=stock_ctx["product_id"],
        batch_number=f"NEW-{stock_ctx['product_id']}",
        expiration_date=date.today() + timedelta(days=40),
    )
    session.add(newer)
    await session.flush()

    stock = StockService(StockRepository(session))
    await stock.add_stock(
        user_id=stock_ctx["user_id"],
        product_id=stock_ctx["product_id"],
        location_id=stock_ctx["location_id"],
        quantity=Decimal("8"),
        lpn_id=stock_ctx["lpn_id"],
        batch_id=stock_ctx["batch_id"],
    )
    await stock.add_stock(
        user_id=stock_ctx["user_id"],
        product_id=stock_ctx["product_id"],
        location_id=stock_ctx["location_b_id"],
        quantity=Decimal("10"),
        lpn_id=stock_ctx["lpn_b_id"],
        batch_id=newer.id,
    )

    client = Client(
        depositor_id=stock_ctx["depositor_id"],
        code=f"C-{stock_ctx['product_id']}",
        name="Клиент",
    )
    session.add(client)
    await session.flush()
    order = OutboundOrder(
        depositor_id=stock_ctx["depositor_id"],
        warehouse_id=stock_ctx["warehouse_id"],
        client_id=client.id,
        number=f"OUT-{stock_ctx['product_id']}",
        order_date=date.today(),
    )
    session.add(order)
    await session.flush()
    session.add(
        OutboundOrderLine(
            order_id=order.id,
            product_id=stock_ctx["product_id"],
            quantity=Decimal("3"),
        )
    )
    await session.flush()

    svc = _picking(session)
    task = await svc.create_from_outbound(
        user_id=stock_ctx["user_id"], outbound_order_id=order.id
    )
    await svc.plan_lines(user_id=stock_ctx["user_id"], task_id=task.id)
    lines = await TaskLineRepository(session).list_by_task(task.id)
    pickable = [ln for ln in lines if ln.from_location_id]
    assert len(pickable) == 1
    assert pickable[0].from_location_id == stock_ctx["location_id"]
    assert pickable[0].batch_id == stock_ctx["batch_id"]
    await svc.pick_line(
        user_id=stock_ctx["user_id"],
        task_line_id=pickable[0].id,
        quantity=pickable[0].plan_qty,
    )
    await svc.complete(user_id=stock_ctx["user_id"], task_id=task.id)

    left_old = await stock.get_available_quantity(
        stock_ctx["product_id"], location_id=stock_ctx["location_id"]
    )
    left_new = await stock.get_available_quantity(
        stock_ctx["product_id"], location_id=stock_ctx["location_b_id"]
    )
    assert left_old == Decimal("5")
    assert left_new == Decimal("10")
