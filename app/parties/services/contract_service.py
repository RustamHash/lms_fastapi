# app/parties/services/contract_service.py

"""Сервис договоров."""

from __future__ import annotations

from app.parties.models import Contract
from app.parties.repository import ContractRepository


class ContractService:
    def __init__(self, repo: ContractRepository) -> None:
        self._repo = repo

    async def get_by_id(self, id: int) -> Contract | None:
        return await self._repo.get_by_id(id)

    async def list_all(self) -> list[Contract]:
        return await self._repo.list_all()

    async def create(self, **kwargs) -> Contract:
        return await self._repo.create(**kwargs)

    async def update(self, id: int, **kwargs) -> Contract | None:
        return await self._repo.update(id, **kwargs)

    async def soft_delete(self, id: int, user_id: int | None = None) -> bool:
        return await self._repo.soft_delete(id, user_id)
