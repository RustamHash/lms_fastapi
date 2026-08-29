"""EventBus — шина событий."""

from __future__ import annotations

import asyncio
import logging
from collections import defaultdict
from typing import Any, Awaitable, Callable

from sqlalchemy.ext.asyncio import AsyncSession

from app.infrastructure.events.event_types import EventTypes

logger = logging.getLogger(__name__)

EventHandler = Callable[[dict[str, Any]], Awaitable[None]]

PENDING_EVENTS_KEY = "_pending_events"

# События, для которых после исчерпания retry ставится Celery ensure_delivery.
_OUTBOUND_DELIVERY_EVENTS = frozenset(
    {
        EventTypes.OUTBOUND_ORDER_CREATED,
        EventTypes.OUTBOUND_ORDER_ACCEPTED_FROM_EXCHANGE,
    }
)

_HANDLER_RETRIES = 3
_RETRY_SLEEP_SEC = 0.05


def schedule_event(session: AsyncSession, event_type: str, data: dict[str, Any]) -> None:
    """Отложить событие до commit сессии (flush в UnitOfWork.__aexit__)."""
    pending: list[tuple[str, dict[str, Any]]] = session.info.setdefault(PENDING_EVENTS_KEY, [])
    pending.append((event_type, {**data, "_event_type": event_type}))


def discard_pending_events(session: AsyncSession) -> None:
    """Сбросить очередь событий (rollback)."""
    session.info.pop(PENDING_EVENTS_KEY, None)


async def flush_pending_events(session: AsyncSession) -> None:
    """Отправить отложенные события после успешного commit."""
    pending: list[tuple[str, dict[str, Any]]] = session.info.pop(PENDING_EVENTS_KEY, [])
    for event_type, data in pending:
        await event_bus.emit(event_type, data)


class EventBus:
    """Простая асинхронная шина событий."""

    def __init__(self) -> None:
        self._handlers: dict[str, list[EventHandler]] = defaultdict(list)

    def subscribe(self, event_type: str, handler: EventHandler) -> None:
        """Подписать обработчик на событие."""
        self._handlers[event_type].append(handler)
        logger.info("Подписчик %s на событие %s", handler.__name__, event_type)

    def unsubscribe(self, event_type: str, handler: EventHandler) -> None:
        """Отписать обработчик."""
        if handler in self._handlers[event_type]:
            self._handlers[event_type].remove(handler)

    async def emit(self, event_type: str, data: dict[str, Any]) -> None:
        """Отправить событие всем подписчикам (до 3 попыток на handler)."""
        handlers = self._handlers.get(event_type, [])
        logger.info("Событие %s: %s", event_type, data)

        for handler in handlers:
            last_exc: Exception | None = None
            for attempt in range(1, _HANDLER_RETRIES + 1):
                try:
                    await handler(data)
                    last_exc = None
                    break
                except Exception as e:
                    last_exc = e
                    logger.error(
                        "Ошибка обработчика %s для события %s (попытка %s/%s): %s",
                        handler.__name__,
                        event_type,
                        attempt,
                        _HANDLER_RETRIES,
                        e,
                    )
                    if attempt < _HANDLER_RETRIES:
                        await asyncio.sleep(_RETRY_SLEEP_SEC)

            if last_exc is not None and event_type in _OUTBOUND_DELIVERY_EVENTS:
                order_id = data.get("order_id")
                if order_id:
                    logger.error(
                        "Исчерпаны retry для %s order_id=%s — очередь Celery ensure_delivery",
                        event_type,
                        order_id,
                    )
                    self._enqueue_ensure_delivery(int(order_id))

    @staticmethod
    def _enqueue_ensure_delivery(order_id: int) -> None:
        try:
            from app.tasks import celery_app

            celery_app.send_task(
                "app.tasks.ensure_delivery_for_outbound",
                args=[order_id],
            )
        except Exception:
            logger.exception(
                "Не удалось поставить Celery ensure_delivery_for_outbound(%s)",
                order_id,
            )


event_bus = EventBus()
