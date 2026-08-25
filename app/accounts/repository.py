# app/accounts/repository.py

"""Репозитории для модуля accounts."""

from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.accounts.models import Audit, Role, User, UserClient, UserDepositor, UserSettings, UserTableSettings, UserListPreset


class UserRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._s = session

    def _alive(self):
        return User.is_deleted.is_(False)

    async def get_by_id(
        self,
        id: int,
        *,
        include_deleted: bool = False,
        with_depositors: bool = False,
    ) -> User | None:
        options = [selectinload(User.roles)]
        if with_depositors:
            options.append(selectinload(User.user_depositors))
            options.append(selectinload(User.user_clients))
        stmt = select(User).where(User.id == id).options(*options)
        if not include_deleted:
            stmt = stmt.where(self._alive())
        return await self._s.scalar(stmt)

    async def get_by_username(
        self, username: str, *, include_deleted: bool = False
    ) -> User | None:
        stmt = (
            select(User)
            .where(User.username == username)
            .options(selectinload(User.roles))
        )
        if not include_deleted:
            stmt = stmt.where(self._alive())
        return await self._s.scalar(stmt)

    async def list_all(self) -> list[User]:
        stmt = (
            select(User)
            .where(self._alive())
            .options(
                selectinload(User.roles),
                selectinload(User.user_depositors),
                selectinload(User.user_clients),
            )
            .order_by(User.id)
        )
        return list(await self._s.scalars(stmt))

    async def create(self, **kwargs) -> User:
        row = User(**kwargs)
        self._s.add(row)
        await self._s.flush()
        await self._s.refresh(row, ["roles", "user_depositors", "user_clients"])
        return row

    async def update(self, id: int, **kwargs) -> User | None:
        row = await self.get_by_id(id, with_depositors=True)
        if row is None:
            return None
        for field, value in kwargs.items():
            setattr(row, field, value)
        await self._s.flush()
        return row

    async def soft_delete(self, id: int, user_id: int | None = None) -> bool:
        row = await self.get_by_id(id)
        if row is None:
            return False
        row.soft_delete(user_id)
        await self._s.flush()
        return True

    async def set_roles(self, user: User, roles: list[Role]) -> User:
        user.roles = roles
        await self._s.flush()
        return user


class RoleRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._s = session

    def _alive(self):
        return Role.is_deleted.is_(False)

    async def get_by_id(self, id: int, *, include_deleted: bool = False) -> Role | None:
        stmt = select(Role).where(Role.id == id)
        if not include_deleted:
            stmt = stmt.where(self._alive())
        return await self._s.scalar(stmt)

    async def get_by_code(self, code: str) -> Role | None:
        stmt = select(Role).where(Role.code == code, self._alive())
        return await self._s.scalar(stmt)

    async def list_by_ids(self, ids: list[int]) -> list[Role]:
        if not ids:
            return []
        stmt = select(Role).where(Role.id.in_(ids), self._alive())
        return list(await self._s.scalars(stmt))

    async def list_all(self) -> list[Role]:
        stmt = select(Role).where(self._alive()).order_by(Role.id)
        return list(await self._s.scalars(stmt))

    async def create(self, **kwargs) -> Role:
        row = Role(**kwargs)
        self._s.add(row)
        await self._s.flush()
        await self._s.refresh(row)
        return row

    async def update(self, id: int, **kwargs) -> Role | None:
        row = await self.get_by_id(id)
        if row is None:
            return None
        for field, value in kwargs.items():
            setattr(row, field, value)
        await self._s.flush()
        return row

    async def soft_delete(self, id: int, user_id: int | None = None) -> bool:
        row = await self.get_by_id(id)
        if row is None:
            return False
        row.soft_delete(user_id)
        await self._s.flush()
        return True


class AuditRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._s = session

    async def get_by_id(self, id: int) -> Audit | None:
        return await self._s.get(Audit, id)

    async def list_all(self, limit: int = 100) -> list[Audit]:
        stmt = select(Audit).order_by(Audit.created_at.desc()).limit(limit)
        return list(await self._s.scalars(stmt))

    async def create(self, **kwargs) -> Audit:
        row = Audit(**kwargs)
        self._s.add(row)
        await self._s.flush()
        return row


class UserSettingsRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._s = session

    async def get_by_id(self, id: int) -> UserSettings | None:
        return await self._s.get(UserSettings, id)

    async def get_by_user(self, user_id: int) -> UserSettings | None:
        stmt = select(UserSettings).where(UserSettings.user_id == user_id)
        return await self._s.scalar(stmt)

    async def list_all(self) -> list[UserSettings]:
        stmt = select(UserSettings)
        return list(await self._s.scalars(stmt))

    async def create(self, **kwargs) -> UserSettings:
        row = UserSettings(**kwargs)
        self._s.add(row)
        await self._s.flush()
        return row

    async def update(self, id: int, **kwargs) -> UserSettings | None:
        row = await self._s.get(UserSettings, id)
        if row is None:
            return None
        for field, value in kwargs.items():
            setattr(row, field, value)
        await self._s.flush()
        return row

    async def soft_delete(self, id: int, user_id: int | None = None) -> bool:
        row = await self._s.get(UserSettings, id)
        if row is None:
            return False
        row.soft_delete(user_id)
        await self._s.flush()
        return True


class UserTableSettingsRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._s = session

    async def get_by_id(self, id: int) -> UserTableSettings | None:
        return await self._s.get(UserTableSettings, id)

    async def get_by_user_and_table(self, user_id: int, table_id: str) -> UserTableSettings | None:
        stmt = select(UserTableSettings).where(UserTableSettings.user_id == user_id, UserTableSettings.table_id == table_id)
        return await self._s.scalar(stmt)

    async def get_or_create(self, user_id: int, table_id: str) -> UserTableSettings:
        row = await self.get_by_user_and_table(user_id, table_id)
        if row:
            return row
        row = UserTableSettings(user_id=user_id, table_id=table_id)
        self._s.add(row)
        await self._s.flush()
        return row

    async def list_all(self) -> list[UserTableSettings]:
        stmt = select(UserTableSettings)
        return list(await self._s.scalars(stmt))

    async def create(self, user_id: int, table_id: str, **kwargs) -> UserTableSettings:
        row = UserTableSettings(user_id=user_id, table_id=table_id, **kwargs)
        self._s.add(row)
        await self._s.flush()
        return row

    async def update(self, user_id: int, table_id: str, **kwargs) -> UserTableSettings | None:
        row = await self.get_by_user_and_table(user_id, table_id)
        if row is None:
            return None
        for field, value in kwargs.items():
            setattr(row, field, value)
        await self._s.flush()
        return row

    async def soft_delete(self, id: int, user_id: int | None = None) -> bool:
        row = await self._s.get(UserTableSettings, id)
        if row is None:
            return False
        row.soft_delete(user_id)
        await self._s.flush()
        return True


class ListPresetRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._s = session

    async def get_by_id(self, id: int) -> UserListPreset | None:
        return await self._s.get(UserListPreset, id)

    async def list_by_user_and_table(self, user_id: int, table_id: str) -> list[UserListPreset]:
        stmt = select(UserListPreset).where(UserListPreset.user_id == user_id, UserListPreset.table_id == table_id)
        return list(await self._s.scalars(stmt))

    async def list_all(self) -> list[UserListPreset]:
        stmt = select(UserListPreset)
        return list(await self._s.scalars(stmt))

    async def create(self, **kwargs) -> UserListPreset:
        row = UserListPreset(**kwargs)
        self._s.add(row)
        await self._s.flush()
        return row

    async def update(self, id: int, **kwargs) -> UserListPreset | None:
        row = await self._s.get(UserListPreset, id)
        if row is None:
            return None
        for field, value in kwargs.items():
            setattr(row, field, value)
        await self._s.flush()
        return row

    async def soft_delete(self, id: int, user_id: int | None = None) -> bool:
        row = await self._s.get(UserListPreset, id)
        if row is None:
            return False
        row.soft_delete(user_id)
        await self._s.flush()
        return True


class UserDepositorRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._s = session

    async def get_by_id(self, id: int) -> UserDepositor | None:
        return await self._s.get(UserDepositor, id)

    async def get_by_user_and_depositor(self, user_id: int, depositor_id: int) -> UserDepositor | None:
        stmt = select(UserDepositor).where(UserDepositor.user_id == user_id, UserDepositor.depositor_id == depositor_id)
        return await self._s.scalar(stmt)

    async def list_by_user(self, user_id: int) -> list[UserDepositor]:
        stmt = select(UserDepositor).where(
            UserDepositor.user_id == user_id,
            UserDepositor.is_deleted.is_(False),
        )
        return list(await self._s.scalars(stmt))

    async def replace_for_user(self, user: User, depositor_ids: list[int]) -> None:
        existing = {
            row.depositor_id: row
            for row in user.user_depositors
        }
        wanted = set(depositor_ids)
        for depositor_id in wanted:
            row = existing.get(depositor_id)
            if row is None:
                self._s.add(UserDepositor(user_id=user.id, depositor_id=depositor_id))
            elif row.is_deleted:
                row.restore()
        for depositor_id, row in existing.items():
            if depositor_id not in wanted and not row.is_deleted:
                row.soft_delete()
        await self._s.flush()
        await self._s.refresh(user, ["user_depositors"])

    async def create(self, **kwargs) -> UserDepositor:
        row = UserDepositor(**kwargs)
        self._s.add(row)
        await self._s.flush()
        return row

    async def update(self, id: int, **kwargs) -> UserDepositor | None:
        row = await self._s.get(UserDepositor, id)
        if row is None:
            return None
        for field, value in kwargs.items():
            setattr(row, field, value)
        await self._s.flush()
        return row

    async def soft_delete(self, id: int, user_id: int | None = None) -> bool:
        row = await self._s.get(UserDepositor, id)
        if row is None:
            return False
        row.soft_delete(user_id)
        await self._s.flush()
        return True


class UserClientRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._s = session

    async def replace_for_user(self, user: User, client_ids: list[int]) -> None:
        existing = {row.client_id: row for row in user.user_clients}
        wanted = set(client_ids)
        for client_id in wanted:
            row = existing.get(client_id)
            if row is None:
                self._s.add(UserClient(user_id=user.id, client_id=client_id))
            elif row.is_deleted:
                row.restore()
        for client_id, row in existing.items():
            if client_id not in wanted and not row.is_deleted:
                row.soft_delete()
        await self._s.flush()
        await self._s.refresh(user, ["user_clients"])
