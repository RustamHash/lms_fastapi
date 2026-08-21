"""EventBus — шина событий."""

from __future__ import annotations

import logging
from collections import defaultdict
from typing import Any, Awaitable, Callable

logger = logging.getLogger(__name__)

EventHandler = Callable[[dict[str, Any]], Awaitable[None]]


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
        """Отправить событие всем подписчикам."""
        handlers = self._handlers.get(event_type, [])
        logger.info("Событие %s: %s", event_type, data)

        for handler in handlers:
            try:
                await handler(data)
            except Exception as e:
                logger.error(
                    "Ошибка обработчика %s для события %s: %s",
                    handler.__name__,
                    event_type,
                    e,
                )


event_bus = EventBus()
