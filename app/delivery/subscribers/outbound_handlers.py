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
        logger.debug(
            "Пропуск ensure_delivery: needs_delivery=false, data=%s", data
        )
        return

    order_id = data.get("order_id")
    if not order_id:
        logger.warning("Событие outbound без order_id: %s", data)
        return

    event_type = data.get("_event_type", "?")
    logger.info(
        "ensure_delivery: событие=%s order_id=%s — создаём DeliveryOrder при необходимости",
        event_type,
        order_id,
    )

    async with UnitOfWork(async_session_factory) as session:
        delivery = await delivery_from_outbound_from_session(session).ensure_for_outbound(
            order_id
        )
        if delivery is None:
            logger.info(
                "ensure_delivery: order_id=%s — доставка не требуется или outbound не найден",
                order_id,
            )
        else:
            logger.info(
                "ensure_delivery: order_id=%s → delivery_order_id=%s",
                order_id,
                delivery.id,
            )


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
