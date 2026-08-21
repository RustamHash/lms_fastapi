"""Сервис уведомлений."""

from __future__ import annotations

from app.notifications.repository import NotificationRepository


class NotificationService:
    def __init__(self, repo: NotificationRepository) -> None:
        self._repo = repo

    async def create(self, user_id: int, title: str, text: str, notification_type: str = "system", link: str = ""):
        return await self._repo.create(
            user_id=user_id,
            title=title,
            text=text,
            notification_type=notification_type,
            link=link,
        )

    async def mark_read(self, notification_id: int):
        from datetime import datetime
        return await self._repo.update(
            notification_id,
            status="read",
            read_at=datetime.now().isoformat(),
        )

    async def mark_all_read(self, user_id: int) -> int:
        return await self._repo.mark_all_read(user_id)

    async def get_unread(self, user_id: int):
        return await self._repo.list_unread(user_id)

    async def list_by_user(self, user_id: int):
        return await self._repo.list_by_user(user_id)
