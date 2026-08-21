"""Репозитории для настроек списков и пресетов."""

from __future__ import annotations

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.accounts.models import UserListPreset, UserTableSettings


class TableSettingsRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._s = session

    async def get_by_user_and_table(
        self, user_id: int, table_id: str
    ) -> UserTableSettings | None:
        stmt = select(UserTableSettings).where(
            UserTableSettings.user_id == user_id,
            UserTableSettings.table_id == table_id,
        )
        return await self._s.scalar(stmt)

    async def create(self, user_id: int, table_id: str, **fields) -> UserTableSettings:
        settings = UserTableSettings(user_id=user_id, table_id=table_id, **fields)
        self._s.add(settings)
        await self._s.flush()
        return settings

    async def update(
        self, user_id: int, table_id: str, **fields
    ) -> UserTableSettings | None:
        settings = await self.get_by_user_and_table(user_id, table_id)
        if settings is None:
            return None
        for key, value in fields.items():
            setattr(settings, key, value)
        await self._s.flush()
        return settings

    async def delete(self, user_id: int, table_id: str) -> bool:
        settings = await self.get_by_user_and_table(user_id, table_id)
        if settings is None:
            return False
        await self._s.delete(settings)
        await self._s.flush()
        return True


class ListPresetRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._s = session

    async def list_by_user_and_table(
        self, user_id: int, table_id: str
    ) -> list[UserListPreset]:
        stmt = (
            select(UserListPreset)
            .where(
                UserListPreset.user_id == user_id,
                UserListPreset.table_id == table_id,
            )
            .order_by(UserListPreset.name)
        )
        return list(await self._s.scalars(stmt))

    async def get_by_id(self, preset_id: int) -> UserListPreset | None:
        return await self._s.get(UserListPreset, preset_id)

    async def create(self, **fields) -> UserListPreset:
        preset = UserListPreset(**fields)
        self._s.add(preset)
        await self._s.flush()
        return preset

    async def update(self, preset_id: int, **fields) -> UserListPreset | None:
        preset = await self.get_by_id(preset_id)
        if preset is None:
            return None
        for key, value in fields.items():
            setattr(preset, key, value)
        await self._s.flush()
        return preset

    async def delete(self, preset_id: int) -> bool:
        preset = await self.get_by_id(preset_id)
        if preset is None:
            return False
        await self._s.delete(preset)
        await self._s.flush()
        return True

    async def clear_default(self, user_id: int, table_id: str) -> None:
        stmt = (
            update(UserListPreset)
            .where(
                UserListPreset.user_id == user_id,
                UserListPreset.table_id == table_id,
            )
            .values(is_default=False)
        )
        await self._s.execute(stmt)
        await self._s.flush()
