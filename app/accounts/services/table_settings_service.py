"""Сервис настроек таблиц."""

from __future__ import annotations

from app.accounts.models import UserTableSettings
from app.accounts.repository import UserTableSettingsRepository


class TableSettingsService:
    def __init__(self, repo: UserTableSettingsRepository) -> None:
        self._repo = repo

    async def get_or_create(self, user_id: int, table_id: str) -> UserTableSettings:
        return await self._repo.get_or_create(user_id, table_id)

    async def get_columns_order(self, user_id: int, table_id: str) -> list[str]:
        settings = await self.get_or_create(user_id, table_id)
        return settings.columns_order or []

    async def get_hidden_columns(self, user_id: int, table_id: str) -> list[str]:
        settings = await self.get_or_create(user_id, table_id)
        return settings.hidden_columns or []

    async def get_column_widths(self, user_id: int, table_id: str) -> dict[str, int]:
        settings = await self.get_or_create(user_id, table_id)
        return settings.column_widths or {}

    async def update(self, user_id: int, table_id: str, **fields) -> UserTableSettings | None:
        return await self._repo.update(user_id, table_id, **fields)
