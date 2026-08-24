# app/parties/services/tariff_service.py

"""Сервис тарифов."""

from __future__ import annotations

from app.parties.models import Tariff
from app.parties.repository import TariffRepository


class TariffService:
    def __init__(self, repo: TariffRepository) -> None:
        self._repo = repo

    async def get_by_id(self, id: int) -> Tariff | None:
        return await self._repo.get_by_id(id)

    async def list_all(self) -> list[Tariff]:
        return await self._repo.list_all()

    async def create(self, **kwargs) -> Tariff:
        return await self._repo.create(**kwargs)

    async def update(self, id: int, **kwargs) -> Tariff | None:
        return await self._repo.update(id, **kwargs)

    async def soft_delete(self, id: int, user_id: int | None = None) -> bool:
        return await self._repo.soft_delete(id, user_id)
