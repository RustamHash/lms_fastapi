"""DeliveryOrder из OutboundOrder."""

from __future__ import annotations

from datetime import date

import pytest
from sqlalchemy import select

from app.delivery.models import DeliveryOrder
from app.delivery.services.from_outbound_service import delivery_from_outbound_from_session
from app.infrastructure.uow import UnitOfWork
from app.orders.models import OutboundOrder
from app.parties.models.client import Client


@pytest.mark.asyncio
async def test_ensure_for_outbound_creates_delivery(session_factory, stock_ctx) -> None:
    outbound_id: int

    async with UnitOfWork(session_factory) as session:
        client = Client(
            depositor_id=stock_ctx["depositor_id"],
            code=f"DLV-{stock_ctx['product_id']}",
            name="Клиент доставки",
        )
        session.add(client)
        await session.flush()

        outbound = OutboundOrder(
            depositor_id=stock_ctx["depositor_id"],
            warehouse_id=stock_ctx["warehouse_id"],
            client_id=client.id,
            number=f"OUT-DLV-{stock_ctx['product_id']}",
            order_date=date.today(),
            needs_delivery=True,
            delivery_contact="Иван +7 900 000-00-00",
        )
        session.add(outbound)
        await session.flush()
        outbound_id = outbound.id

    async with UnitOfWork(session_factory) as session:
        delivery = await delivery_from_outbound_from_session(session).ensure_for_outbound(
            outbound_id
        )
        assert delivery is not None
        assert delivery.outbound_order_id == outbound_id
        assert delivery.contact_person.startswith("Иван")

    async with session_factory() as session:
        rows = list(
            await session.scalars(
                select(DeliveryOrder).where(
                    DeliveryOrder.outbound_order_id == outbound_id
                )
            )
        )
        assert len(rows) == 1


@pytest.mark.asyncio
async def test_ensure_for_outbound_idempotent(session_factory, stock_ctx) -> None:
    outbound_id: int

    async with UnitOfWork(session_factory) as session:
        client = Client(
            depositor_id=stock_ctx["depositor_id"],
            code=f"IDM-{stock_ctx['product_id']}",
            name="Клиент",
        )
        session.add(client)
        await session.flush()
        outbound = OutboundOrder(
            depositor_id=stock_ctx["depositor_id"],
            warehouse_id=stock_ctx["warehouse_id"],
            client_id=client.id,
            number=f"OUT-IDM-{stock_ctx['product_id']}",
            order_date=date.today(),
            needs_delivery=True,
        )
        session.add(outbound)
        await session.flush()
        outbound_id = outbound.id

    async with UnitOfWork(session_factory) as session:
        svc = delivery_from_outbound_from_session(session)
        first = await svc.ensure_for_outbound(outbound_id)
        second = await svc.ensure_for_outbound(outbound_id)
        assert first is not None
        assert second is not None
        assert first.id == second.id


@pytest.mark.asyncio
async def test_ensure_skips_without_needs_delivery(session_factory, stock_ctx) -> None:
    outbound_id: int

    async with UnitOfWork(session_factory) as session:
        client = Client(
            depositor_id=stock_ctx["depositor_id"],
            code=f"PKP-{stock_ctx['product_id']}",
            name="Самовывоз",
        )
        session.add(client)
        await session.flush()
        outbound = OutboundOrder(
            depositor_id=stock_ctx["depositor_id"],
            warehouse_id=stock_ctx["warehouse_id"],
            client_id=client.id,
            number=f"OUT-PKP-{stock_ctx['product_id']}",
            order_date=date.today(),
            needs_delivery=False,
        )
        session.add(outbound)
        await session.flush()
        outbound_id = outbound.id

    async with UnitOfWork(session_factory) as session:
        delivery = await delivery_from_outbound_from_session(session).ensure_for_outbound(
            outbound_id
        )
        assert delivery is None
