"""Подписчики delivery на события outbound."""

from __future__ import annotations

import logging

from app.core.database import async_session_factory
from app.delivery.services.from_outbound_service import delivery_from_outbound_from_session
from app.infrastructure.events import event_bus
from app.infrastructure.events.event_types import EventTypes
from app.infrastructure.uow import UnitOfWork

logger = logging.getLogger(__name__)


async def handle_outbound_needs_delivery(data: dict) -> None:
    """Создать заявку на доставку после commit исходящего заказа."""
    if not data.get("needs_delivery"):
        return

    order_id = data.get("order_id")
    if not order_id:
        logger.warning("Событие outbound без order_id: %s", data)
        return

    async with UnitOfWork(async_session_factory) as session:
        await delivery_from_outbound_from_session(session).ensure_for_outbound(order_id)


def setup_delivery_subscribers() -> None:
    """Подписать обработчики delivery на события outbound. Идемпотентно."""
    handlers = event_bus._handlers.get(EventTypes.OUTBOUND_ORDER_ACCEPTED_FROM_EXCHANGE, [])
    if handle_outbound_needs_delivery in handlers:
        return
    event_bus.subscribe(
        EventTypes.OUTBOUND_ORDER_ACCEPTED_FROM_EXCHANGE,
        handle_outbound_needs_delivery,
    )
    event_bus.subscribe(
        EventTypes.OUTBOUND_ORDER_CREATED,
        handle_outbound_needs_delivery,
    )
    logger.info("Подписчики delivery зарегистрированы")
