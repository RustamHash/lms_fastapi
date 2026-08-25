"""Inbound → приёмка → остаток вырос."""

from __future__ import annotations

from datetime import date
from decimal import Decimal

from sqlalchemy.ext.asyncio import AsyncSession

from app.orders.models import InboundOrder, InboundOrderLine
from app.orders.repository import InboundOrderLineRepository, InboundOrderRepository
from app.parties.models.client import Client
from app.warehouse.repository import (
    BatchRepository,
    LocationRepository,
    LPNRepository,
    ProductRepository,
    ReceivingDiscrepancyRepository,
    StockRepository,
    TaskLineRepository,
    TaskRepository,
)
from app.warehouse.services.batch_service import BatchService
from app.warehouse.services.lpn_service import LPNService
from app.warehouse.services.placement_service import PlacementService
from app.warehouse.services.receiving_service import ReceivingService
from app.warehouse.services.stock_service import StockService


def _receiving(session: AsyncSession) -> ReceivingService:
    return ReceivingService(
        tasks=TaskRepository(session),
        lines=TaskLineRepository(session),
        inbound=InboundOrderRepository(session),
        inbound_lines=InboundOrderLineRepository(session),
        stock=StockService(StockRepository(session)),
        stock_repo=StockRepository(session),
        batches=BatchService(BatchRepository(session)),
        lpns=LPNService(LPNRepository(session)),
        products=ProductRepository(session),
        locations=LocationRepository(session),
        placement=PlacementService(session),
        discrepancies=ReceivingDiscrepancyRepository(session),
    )


async def test_inbound_receive_grows_stock(session: AsyncSession, stock_ctx: dict) -> None:
    supplier = Client(
        depositor_id=stock_ctx["depositor_id"],
        code=f"S-{stock_ctx['product_id']}",
        name="Поставщик",
    )
    session.add(supplier)
    await session.flush()
    order = InboundOrder(
        depositor_id=stock_ctx["depositor_id"],
        warehouse_id=stock_ctx["warehouse_id"],
        supplier_id=supplier.id,
        supplier_code=supplier.code,
        number=f"IN-{stock_ctx['product_id']}",
        loc_code="0001",
        order_date=date.today(),
    )
    session.add(order)
    await session.flush()
    session.add(
        InboundOrderLine(
            order_id=order.id,
            product_id=stock_ctx["product_id"],
            quantity=Decimal("10"),
            batch_number="LOT-1",
        )
    )
    await session.flush()

    svc = _receiving(session)
    task = await svc.create_from_inbound(
        user_id=stock_ctx["user_id"],
        inbound_order_id=order.id,
        receiving_location_id=stock_ctx["location_id"],
    )
    lines = await TaskLineRepository(session).list_by_task(task.id)
    assert len(lines) == 1

    await svc.receive_line(
        user_id=stock_ctx["user_id"],
        task_line_id=lines[0].id,
        quantity=Decimal("10"),
        batch_number="LOT-1",
    )
    await svc.complete(user_id=stock_ctx["user_id"], task_id=task.id)

    available = await StockService(StockRepository(session)).get_available_quantity(
        stock_ctx["product_id"], location_id=stock_ctx["location_id"]
    )
    assert available == Decimal("10")
