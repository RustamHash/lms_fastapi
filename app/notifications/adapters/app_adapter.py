"""Адаптер доставки в приложение."""

from __future__ import annotations

from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from app.notifications.adapters.base import BaseAdapter
from app.notifications.models import Notification


class AppAdapter(BaseAdapter):
    """Создает уведомление в БД."""

    channel = "app"

    def __init__(self, session: AsyncSession) -> None:
        self._s = session

    async def send(self, recipient: dict[str, Any], notification: dict[str, Any]) -> None:
        """Создать уведомление в БД."""
        notify = Notification(
            user_id=recipient["user_id"],
            title=notification["title"],
            text=notification["text"],
            notification_type=notification.get("notification_type", "system"),
            link=notification.get("link", ""),
        )
        self._s.add(notify)
        await self._s.flush()
