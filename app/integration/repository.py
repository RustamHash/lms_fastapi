# app/integration/repository.py

"""Репозитории для модуля integration."""

from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.accounts.scope import DataScope
from app.integration.models import IntegrationError, IntegrationLog, IntegrationProfile


class IntegrationProfileRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._s = session

    async def get_by_id(
        self, id: int, scope: DataScope | None = None
    ) -> IntegrationProfile | None:
        row = await self._s.get(IntegrationProfile, id)
        if row is None or row.is_deleted:
            return None
        if scope is not None and not scope.allows_depositor(row.depositor_id):
            return None
        return row

    async def list_all(
        self, scope: DataScope | None = None
    ) -> list[IntegrationProfile]:
        stmt = select(IntegrationProfile).where(
            IntegrationProfile.is_deleted.is_(False)
        )
        if scope is not None:
            stmt = scope.filter_depositor(stmt, IntegrationProfile.depositor_id)
        return list(await self._s.scalars(stmt))

    async def list_active(self) -> list[IntegrationProfile]:
        stmt = select(IntegrationProfile).where(
            IntegrationProfile.is_active.is_(True),
            IntegrationProfile.is_deleted.is_(False),
        )
        return list(await self._s.scalars(stmt))

    async def get_active_with_out_path(
        self, depositor_id: int
    ) -> IntegrationProfile | None:
        """Первый активный профиль поклажедателя с config.ftp.out_path."""
        profiles = await self.list_active()
        for profile in profiles:
            if profile.depositor_id != depositor_id:
                continue
            ftp = (profile.config or {}).get("ftp") or {}
            if str(ftp.get("out_path") or "").strip():
                return profile
        return None

    async def create(self, **kwargs) -> IntegrationProfile:
        row = IntegrationProfile(**kwargs)
        self._s.add(row)
        await self._s.flush()
        await self._s.refresh(row)
        return row

    async def update(self, id: int, **kwargs) -> IntegrationProfile | None:
        row = await self.get_by_id(id)
        if row is None:
            return None
        for field, value in kwargs.items():
            setattr(row, field, value)
        await self._s.flush()
        await self._s.refresh(row)
        return row

    async def soft_delete(self, id: int, user_id: int | None = None) -> bool:
        row = await self.get_by_id(id)
        if row is None:
            return False
        row.soft_delete(user_id)
        await self._s.flush()
        return True


class IntegrationLogRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._s = session

    async def get_by_id(self, id: int) -> IntegrationLog | None:
        return await self._s.get(IntegrationLog, id)

    async def get_by_task_id(self, task_id: str) -> IntegrationLog | None:
        stmt = select(IntegrationLog).where(IntegrationLog.task_id == task_id)
        return await self._s.scalar(stmt)

    async def list_all(self) -> list[IntegrationLog]:
        stmt = select(IntegrationLog).order_by(IntegrationLog.created_at.desc())
        return list(await self._s.scalars(stmt))

    async def create(self, **kwargs) -> IntegrationLog:
        row = IntegrationLog(**kwargs)
        self._s.add(row)
        await self._s.flush()
        return row

    async def update(self, id: int, **kwargs) -> IntegrationLog | None:
        row = await self._s.get(IntegrationLog, id)
        if row is None:
            return None
        for field, value in kwargs.items():
            setattr(row, field, value)
        await self._s.flush()
        return row


class IntegrationErrorRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._s = session

    async def get_by_id(self, id: int) -> IntegrationError | None:
        return await self._s.get(IntegrationError, id)

    async def list_all(self) -> list[IntegrationError]:
        return list(await self._s.scalars(select(IntegrationError)))

    async def list_by_log(self, log_id: int) -> list[IntegrationError]:
        stmt = select(IntegrationError).where(IntegrationError.log_id == log_id)
        return list(await self._s.scalars(stmt))

    async def create(self, **kwargs) -> IntegrationError:
        row = IntegrationError(**kwargs)
        self._s.add(row)
        await self._s.flush()
        return row
