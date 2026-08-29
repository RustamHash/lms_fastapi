# app/parties/services/depositor_service.py

"""Сервис поклажедателей."""

from __future__ import annotations

from app.accounts.scope import DataScope
from app.parties.models import Depositor
from app.parties.repository import DepositorRepository


class DepositorService:
    def __init__(self, repo: DepositorRepository) -> None:
        self._repo = repo

    async def get_by_id(
        self, id: int, scope: DataScope | None = None
    ) -> Depositor | None:
        return await self._repo.get_by_id(id, scope=scope)

    async def list_all(self, scope: DataScope | None = None) -> list[Depositor]:
        return await self._repo.list_all(scope=scope)

    async def create(self, **kwargs) -> Depositor:
        return await self._repo.create(**kwargs)

    async def update(self, id: int, **kwargs) -> Depositor | None:
        return await self._repo.update(id, **kwargs)

    async def soft_delete(self, id: int, user_id: int | None = None) -> bool:
        return await self._repo.soft_delete(id, user_id)
