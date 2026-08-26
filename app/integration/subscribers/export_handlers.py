"""Подписчики выгрузки ответного XML на события заказов/заданий."""

from __future__ import annotations

import logging

from app.core.database import async_session_factory
from app.infrastructure.events import event_bus
from app.infrastructure.events.event_types import EventTypes
from app.infrastructure.uow import UnitOfWork
from app.integration.services.export_service import export_from_session

logger = logging.getLogger(__name__)


async def handle_inbound_accepted_export(data: dict) -> None:
    order_id = data.get("order_id")
    if not order_id:
        return
    async with UnitOfWork(async_session_factory) as session:
        await export_from_session(session).export_pordrsp(int(order_id))


async def handle_outbound_accepted_export(data: dict) -> None:
    order_id = data.get("order_id")
    if not order_id:
        return
    async with UnitOfWork(async_session_factory) as session:
        await export_from_session(session).export_ordrsp(int(order_id))


async def handle_receiving_completed_export(data: dict) -> None:
    order_id = data.get("inbound_order_id")
    task_id = data.get("task_id")
    if not order_id or not task_id:
        return
    async with UnitOfWork(async_session_factory) as session:
        await export_from_session(session).export_recadv(
            order_id=int(order_id), task_id=int(task_id)
        )


async def handle_picking_completed_export(data: dict) -> None:
    order_id = data.get("outbound_order_id")
    task_id = data.get("task_id")
    if not order_id or not task_id:
        return
    async with UnitOfWork(async_session_factory) as session:
        await export_from_session(session).export_desadv(
            order_id=int(order_id), task_id=int(task_id)
        )


def setup_export_subscribers() -> None:
    handlers = event_bus._handlers.get(
        EventTypes.INBOUND_ORDER_ACCEPTED_FROM_EXCHANGE, []
    )
    if handle_inbound_accepted_export in handlers:
        return
    event_bus.subscribe(
        EventTypes.INBOUND_ORDER_ACCEPTED_FROM_EXCHANGE,
        handle_inbound_accepted_export,
    )
    event_bus.subscribe(
        EventTypes.OUTBOUND_ORDER_ACCEPTED_FROM_EXCHANGE,
        handle_outbound_accepted_export,
    )
    event_bus.subscribe(
        EventTypes.RECEIVING_TASK_COMPLETED,
        handle_receiving_completed_export,
    )
    event_bus.subscribe(
        EventTypes.PICKING_TASK_COMPLETED,
        handle_picking_completed_export,
    )
    logger.info("Подписчики export зарегистрированы")
