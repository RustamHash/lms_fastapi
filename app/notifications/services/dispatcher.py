"""Диспетчер уведомлений — подписчик на события."""

from __future__ import annotations

import logging

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.accounts.models import Role, User
from app.infrastructure.events import event_bus
from app.infrastructure.events.event_types import EventTypes
from app.notifications.adapters import AppAdapter, EmailAdapter
from app.notifications.models import NotificationRule

logger = logging.getLogger(__name__)


class NotificationDispatcher:
    """При событии читает правила и отправляет уведомления."""

    def __init__(self, session: AsyncSession) -> None:
        self._s = session
        self._app_adapter = AppAdapter(session)
        self._email_adapter = EmailAdapter()

    async def handle_event(self, data: dict) -> None:
        """Обработать событие — найти правила и отправить."""
        event_type = data.get("_event_type", "")

        # Найти активные правила для события
        stmt = select(NotificationRule).where(
            NotificationRule.event_type == event_type,
            NotificationRule.is_active.is_(True),
        )
        rules = list(await self._s.scalars(stmt))

        for rule in rules:
            recipients = await self._get_recipients(rule)
            notification = self._build_notification(event_type, data)

            for recipient in recipients:
                if rule.channel == "app":
                    await self._app_adapter.send(recipient, notification)
                elif rule.channel == "email":
                    await self._email_adapter.send(recipient, notification)

    async def _get_recipients(self, rule: NotificationRule) -> list[dict]:
        """Получить получателей по правилу."""
        if rule.recipient_type == "user" and rule.recipient_id:
            user = await self._s.get(User, rule.recipient_id)
            if user:
                return [{"user_id": user.id, "email": user.email}]

        elif rule.recipient_type == "role" and rule.role_code:
            stmt = (
                select(User)
                .join(User.roles)
                .where(Role.code == rule.role_code, User.is_active.is_(True))
            )
            users = list(await self._s.scalars(stmt))
            return [{"user_id": u.id, "email": u.email} for u in users]

        return []

    def _build_notification(self, event_type: str, data: dict) -> dict:
        """Создать текст уведомления на основе события."""
        templates = {
            EventTypes.IMPORT_COMPLETED: {
                "title": "Импорт завершен",
                "text": f"Импорт завершен. Создано документов: {data.get('documents_created', 0)}",
                "notification_type": "info",
            },
            EventTypes.DELIVERY_ORDER_CREATED: {
                "title": "Новая заявка на доставку",
                "text": f"Создана заявка №{data.get('order_number', '')}",
                "notification_type": "info",
            },
            EventTypes.ROUTE_ASSIGNED: {
                "title": "Назначен маршрут",
                "text": f"Вы назначены на маршрут №{data.get('route_number', '')}",
                "notification_type": "info",
                "link": f"/routes/{data.get('route_id', '')}",
            },
        }
        return templates.get(
            event_type,
            {
                "title": "Событие",
                "text": str(data),
                "notification_type": "system",
            },
        )


def setup_notification_dispatcher(session: AsyncSession) -> None:
    """Подписать диспетчер на все события."""
    dispatcher = NotificationDispatcher(session)

    event_bus.subscribe(EventTypes.IMPORT_COMPLETED, dispatcher.handle_event)
    event_bus.subscribe(EventTypes.DELIVERY_ORDER_CREATED, dispatcher.handle_event)
    event_bus.subscribe(EventTypes.ROUTE_ASSIGNED, dispatcher.handle_event)
