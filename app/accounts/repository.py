"""Репозиторий для модуля accounts."""

from __future__ import annotations

from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.accounts.models import Audit, Role, User, UserSettings, UserTableSettings


class UserRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._s = session

    async def get_by_id(self, user_id: int) -> User | None:
        return await self._s.get(User, user_id)

    async def get_by_username(self, username: str) -> User | None:
        stmt = select(User).where(User.username == username)
        return await self._s.scalar(stmt)

    async def create(self, **kwargs) -> User:
        user = User(**kwargs)
        self._s.add(user)
        await self._s.flush()
        await self._s.refresh(user)
        return user

    async def list_all(self) -> list[User]:
        stmt = select(User).where(User.is_deleted.is_(False))
        return list(await self._s.scalars(stmt))

    async def update(self, user_id: int, **kwargs) -> User | None:
        user = await self._s.get(User, user_id)
        if user is None:
            return None
        for field, value in kwargs.items():
            setattr(user, field, value)
        await self._s.flush()
        return user


class RoleRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._s = session

    async def get_by_id(self, role_id: int) -> Role | None:
        return await self._s.get(Role, role_id)

    async def get_by_code(self, code: str) -> Role | None:
        stmt = select(Role).where(Role.code == code)
        return await self._s.scalar(stmt)

    async def create(self, **kwargs) -> Role:
        role = Role(**kwargs)
        self._s.add(role)
        await self._s.flush()
        return role

    async def list_all(self) -> list[Role]:
        stmt = select(Role).where(Role.is_deleted.is_(False))
        return list(await self._s.scalars(stmt))

    async def update(self, role_id: int, **kwargs) -> Role | None:
        role = await self._s.get(Role, role_id)
        if role is None:
            return None
        for field, value in kwargs.items():
            setattr(role, field, value)
        await self._s.flush()
        return role


class AuditRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._s = session

    async def create(self, **kwargs) -> Audit:
        audit = Audit(**kwargs)
        self._s.add(audit)
        await self._s.flush()
        return audit

    async def list_by_user(self, user_id: int, limit: int = 100) -> list[Audit]:
        stmt = select(Audit).where(Audit.user_id == user_id).order_by(Audit.created_at.desc()).limit(limit)
        return list(await self._s.scalars(stmt))


class UserSettingsRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._s = session

    async def get_by_user(self, user_id: int) -> UserSettings | None:
        stmt = select(UserSettings).where(UserSettings.user_id == user_id)
        return await self._s.scalar(stmt)

    async def get_or_create(self, user_id: int) -> UserSettings:
        settings = await self.get_by_user(user_id)
        if settings:
            return settings
        settings = UserSettings(user_id=user_id)
        self._s.add(settings)
        await self._s.flush()
        return settings

    async def update(self, user_id: int, **kwargs) -> UserSettings | None:
        settings = await self.get_by_user(user_id)
        if settings is None:
            return None
        for field, value in kwargs.items():
            setattr(settings, field, value)
        await self._s.flush()
        return settings


class UserTableSettingsRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._s = session

    async def get_by_user_and_table(self, user_id: int, table_id: str) -> UserTableSettings | None:
        stmt = select(UserTableSettings).where(
            UserTableSettings.user_id == user_id,
            UserTableSettings.table_id == table_id,
        )
        return await self._s.scalar(stmt)

    async def get_or_create(self, user_id: int, table_id: str) -> UserTableSettings:
        settings = await self.get_by_user_and_table(user_id, table_id)
        if settings:
            return settings
        settings = UserTableSettings(user_id=user_id, table_id=table_id)
        self._s.add(settings)
        await self._s.flush()
        return settings

    async def update(self, user_id: int, table_id: str, **kwargs) -> UserTableSettings | None:
        settings = await self.get_by_user_and_table(user_id, table_id)
        if settings is None:
            return None
        for field, value in kwargs.items():
            setattr(settings, field, value)
        await self._s.flush()
        return settings
