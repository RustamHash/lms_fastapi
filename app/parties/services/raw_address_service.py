# app/parties/services/raw_address_service.py

"""Сервис сырых адресов (алиасов)."""

from __future__ import annotations

from app.parties.models import RawAddress
from app.parties.repository import RawAddressRepository


class RawAddressService:
    def __init__(self, repo: RawAddressRepository) -> None:
        self._repo = repo

    async def get_by_id(self, id: int) -> RawAddress | None:
        return await self._repo.get_by_id(id)

    async def list_all(self) -> list[RawAddress]:
        return await self._repo.list_all()

    async def create(self, **kwargs) -> RawAddress:
        return await self._repo.create(**kwargs)

    async def update(self, id: int, **kwargs) -> RawAddress | None:
        return await self._repo.update(id, **kwargs)

    async def soft_delete(self, id: int, user_id: int | None = None) -> bool:
        return await self._repo.soft_delete(id, user_id)
