"""Репозитории для модуля notifications."""

from __future__ import annotations

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.notifications.models import Notification, NotificationRule


class NotificationRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._s = session

    async def get_by_id(self, notification_id: int) -> Notification | None:
        return await self._s.get(Notification, notification_id)

    async def list_by_user(self, user_id: int) -> list[Notification]:
        stmt = select(Notification).where(Notification.user_id == user_id)
        return list(await self._s.scalars(stmt))

    async def list_unread(self, user_id: int) -> list[Notification]:
        stmt = select(Notification).where(
            Notification.user_id == user_id,
            Notification.status == "pending",
        )
        return list(await self._s.scalars(stmt))

    async def create(self, **kwargs) -> Notification:
        notification = Notification(**kwargs)
        self._s.add(notification)
        await self._s.flush()
        return notification

    async def update(self, notification_id: int, **kwargs) -> Notification | None:
        notification = await self.get_by_id(notification_id)
        if notification is None:
            return None
        for field, value in kwargs.items():
            setattr(notification, field, value)
        await self._s.flush()
        return notification

    async def mark_all_read(self, user_id: int) -> int:
        from datetime import datetime
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

    async def delete(self, notification_id: int) -> bool:
        notification = await self.get_by_id(notification_id)
        if notification is None:
            return False
        await self._s.delete(notification)
        await self._s.flush()
        return True


class NotificationRuleRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._s = session

    async def get_by_id(self, rule_id: int) -> NotificationRule | None:
        return await self._s.get(NotificationRule, rule_id)

    async def list_all(self) -> list[NotificationRule]:
        stmt = select(NotificationRule)
        return list(await self._s.scalars(stmt))

    async def list_active_by_event(self, event_type: str) -> list[NotificationRule]:
        stmt = select(NotificationRule).where(
            NotificationRule.event_type == event_type,
            NotificationRule.is_active.is_(True),
        )
        return list(await self._s.scalars(stmt))

    async def create(self, **kwargs) -> NotificationRule:
        rule = NotificationRule(**kwargs)
        self._s.add(rule)
        await self._s.flush()
        return rule

    async def update(self, rule_id: int, **kwargs) -> NotificationRule | None:
        rule = await self.get_by_id(rule_id)
        if rule is None:
            return None
        for field, value in kwargs.items():
            setattr(rule, field, value)
        await self._s.flush()
        return rule

    async def delete(self, rule_id: int) -> bool:
        rule = await self.get_by_id(rule_id)
        if rule is None:
            return False
        await self._s.delete(rule)
        await self._s.flush()
        return True
