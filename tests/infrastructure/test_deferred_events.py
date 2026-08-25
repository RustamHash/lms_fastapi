"""Deferred emit: события после commit UoW."""

from __future__ import annotations

import pytest

from app.infrastructure.events import event_bus, schedule_event
from app.infrastructure.events.event_types import EventTypes
from app.infrastructure.uow import UnitOfWork


@pytest.mark.asyncio
async def test_schedule_event_emits_after_commit(session_factory) -> None:
    received: list[dict] = []

    async def handler(data: dict) -> None:
        received.append(data)

    event_bus.subscribe(EventTypes.OUTBOUND_ORDER_CREATED, handler)
    try:
        async with UnitOfWork(session_factory) as session:
            schedule_event(
                session,
                EventTypes.OUTBOUND_ORDER_CREATED,
                {"order_id": 1, "needs_delivery": True},
            )
            assert received == []

        assert len(received) == 1
        assert received[0]["order_id"] == 1
        assert received[0]["_event_type"] == EventTypes.OUTBOUND_ORDER_CREATED
    finally:
        event_bus.unsubscribe(EventTypes.OUTBOUND_ORDER_CREATED, handler)


@pytest.mark.asyncio
async def test_schedule_event_discarded_on_rollback(session_factory) -> None:
    received: list[dict] = []

    async def handler(data: dict) -> None:
        received.append(data)

    event_bus.subscribe(EventTypes.OUTBOUND_ORDER_CREATED, handler)
    try:
        with pytest.raises(RuntimeError):
            async with UnitOfWork(session_factory) as session:
                schedule_event(
                    session,
                    EventTypes.OUTBOUND_ORDER_CREATED,
                    {"order_id": 2, "needs_delivery": True},
                )
                raise RuntimeError("rollback")

        assert received == []
    finally:
        event_bus.unsubscribe(EventTypes.OUTBOUND_ORDER_CREATED, handler)
