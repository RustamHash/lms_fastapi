"""Сервис уведомлений."""

from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.notifications.models import Notification


class NotificationService:
    def __init__(self, session: AsyncSession) -> None:
        self._s = session

    async def create(
        self,
        user_id: int,
        title: str,
        text: str,
        notification_type: str = "system",
        link: str = "",
    ) -> Notification:
        notification = Notification(
            user_id=user_id,
            title=title,
            text=text,
            notification_type=notification_type,
            link=link,
        )
        self._s.add(notification)
        await self._s.flush()
        return notification

    async def mark_read(self, notification_id: int) -> Notification | None:
        notification = await self._s.get(Notification, notification_id)
        if notification is None:
            return None
        from datetime import datetime

        notification.status = "read"
        notification.read_at = datetime.now().isoformat()
        await self._s.flush()
        return notification

    async def mark_all_read(self, user_id: int) -> int:
        from sqlalchemy import update

        stmt = (
            update(Notification)
            .where(
                Notification.user_id == user_id,
                Notification.status == "pending",
            )
            .values(status="read", read_at=datetime.now().isoformat())
        )
        result = await self._s.execute(stmt)
        return result.rowcount

    async def get_unread(self, user_id: int) -> list[Notification]:
        stmt = select(Notification).where(
            Notification.user_id == user_id,
            Notification.status == "pending",
            Notification.is_deleted.is_(False),
        )
        return list(await self._s.scalars(stmt))

    async def list_by_user(self, user_id: int) -> list[Notification]:
        stmt = select(Notification).where(
            Notification.user_id == user_id,
            Notification.is_deleted.is_(False),
        )
        return list(await self._s.scalars(stmt))
