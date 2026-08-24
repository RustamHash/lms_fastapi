# app/notifications/repository.py

"""Репозитории для модуля notifications."""

from __future__ import annotations

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.notifications.models import Notification, NotificationRule


class NotificationRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._s = session

    async def get_by_id(self, id: int) -> Notification | None:
        return await self._s.get(Notification, id)

    async def list_all(self) -> list[Notification]:
        stmt = select(Notification)
        return list(await self._s.scalars(stmt))

    async def list_by_user(self, user_id: int) -> list[Notification]:
        stmt = select(Notification).where(Notification.user_id == user_id)
        return list(await self._s.scalars(stmt))

    async def list_unread(self, user_id: int) -> list[Notification]:
        stmt = select(Notification).where(Notification.user_id == user_id, Notification.status == "pending")
        return list(await self._s.scalars(stmt))

    async def create(self, **kwargs) -> Notification:
        row = Notification(**kwargs)
        self._s.add(row)
        await self._s.flush()
        return row

    async def update(self, id: int, **kwargs) -> Notification | None:
        row = await self._s.get(Notification, id)
        if row is None:
            return None
        for field, value in kwargs.items():
            setattr(row, field, value)
        await self._s.flush()
        return row

    async def mark_all_read(self, user_id: int) -> int:
        from datetime import datetime
        stmt = update(Notification).where(Notification.user_id == user_id, Notification.status == "pending").values(status="read", read_at=datetime.now().isoformat())
        result = await self._s.execute(stmt)
        return result.rowcount

    async def soft_delete(self, id: int, user_id: int | None = None) -> bool:
        row = await self._s.get(Notification, id)
        if row is None:
            return False
        row.soft_delete(user_id)
        await self._s.flush()
        return True


class NotificationRuleRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._s = session

    async def get_by_id(self, id: int) -> NotificationRule | None:
        return await self._s.get(NotificationRule, id)

    async def list_all(self) -> list[NotificationRule]:
        stmt = select(NotificationRule)
        return list(await self._s.scalars(stmt))

    async def list_active_by_event(self, event_type: str) -> list[NotificationRule]:
        stmt = select(NotificationRule).where(NotificationRule.event_type == event_type, NotificationRule.is_active.is_(True))
        return list(await self._s.scalars(stmt))

    async def create(self, **kwargs) -> NotificationRule:
        row = NotificationRule(**kwargs)
        self._s.add(row)
        await self._s.flush()
        return row

    async def update(self, id: int, **kwargs) -> NotificationRule | None:
        row = await self._s.get(NotificationRule, id)
        if row is None:
            return None
        for field, value in kwargs.items():
            setattr(row, field, value)
        await self._s.flush()
        return row

    async def soft_delete(self, id: int, user_id: int | None = None) -> bool:
        row = await self._s.get(NotificationRule, id)
        if row is None:
            return False
        row.soft_delete(user_id)
        await self._s.flush()
        return True
