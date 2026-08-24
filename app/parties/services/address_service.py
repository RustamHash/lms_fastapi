# app/parties/services/address_service.py

"""Сервис адресов."""

from __future__ import annotations

from app.parties.models import Address
from app.parties.repository import AddressRepository


class AddressService:
    def __init__(self, repo: AddressRepository) -> None:
        self._repo = repo

    async def get_by_id(self, id: int) -> Address | None:
        return await self._repo.get_by_id(id)

    async def list_all(self) -> list[Address]:
        return await self._repo.list_all()

    async def create(self, **kwargs) -> Address:
        return await self._repo.create(**kwargs)

    async def update(self, id: int, **kwargs) -> Address | None:
        return await self._repo.update(id, **kwargs)

    async def soft_delete(self, id: int, user_id: int | None = None) -> bool:
        return await self._repo.soft_delete(id, user_id)
