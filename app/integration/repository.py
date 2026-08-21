"""Репозитории для модуля integration."""

from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.integration.models import IntegrationError, IntegrationLog, IntegrationProfile


class IntegrationProfileRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._s = session

    async def get_by_id(self, profile_id: int) -> IntegrationProfile | None:
        return await self._s.get(IntegrationProfile, profile_id)

    async def list_all(self) -> list[IntegrationProfile]:
        stmt = select(IntegrationProfile)
        return list(await self._s.scalars(stmt))

    async def list_active(self) -> list[IntegrationProfile]:
        stmt = select(IntegrationProfile).where(IntegrationProfile.is_active.is_(True))
        return list(await self._s.scalars(stmt))

    async def create(self, **kwargs) -> IntegrationProfile:
        profile = IntegrationProfile(**kwargs)
        self._s.add(profile)
        await self._s.flush()
        return profile

    async def update(self, profile_id: int, **kwargs) -> IntegrationProfile | None:
        profile = await self.get_by_id(profile_id)
        if profile is None:
            return None
        for field, value in kwargs.items():
            setattr(profile, field, value)
        await self._s.flush()
        return profile

    async def delete(self, profile_id: int) -> bool:
        profile = await self.get_by_id(profile_id)
        if profile is None:
            return False
        await self._s.delete(profile)
        await self._s.flush()
        return True


class IntegrationLogRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._s = session

    async def get_by_id(self, log_id: int) -> IntegrationLog | None:
        return await self._s.get(IntegrationLog, log_id)

    async def get_by_task_id(self, task_id: str) -> IntegrationLog | None:
        stmt = select(IntegrationLog).where(IntegrationLog.task_id == task_id)
        return await self._s.scalar(stmt)

    async def list_all(self) -> list[IntegrationLog]:
        stmt = select(IntegrationLog).order_by(IntegrationLog.created_at.desc())
        return list(await self._s.scalars(stmt))

    async def create(self, **kwargs) -> IntegrationLog:
        log = IntegrationLog(**kwargs)
        self._s.add(log)
        await self._s.flush()
        return log

    async def update(self, log_id: int, **kwargs) -> IntegrationLog | None:
        log = await self.get_by_id(log_id)
        if log is None:
            return None
        for field, value in kwargs.items():
            setattr(log, field, value)
        await self._s.flush()
        return log


class IntegrationErrorRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._s = session

    async def list_by_log(self, log_id: int) -> list[IntegrationError]:
        stmt = select(IntegrationError).where(IntegrationError.log_id == log_id)
        return list(await self._s.scalars(stmt))

    async def create(self, **kwargs) -> IntegrationError:
        error = IntegrationError(**kwargs)
        self._s.add(error)
        await self._s.flush()
        return error
