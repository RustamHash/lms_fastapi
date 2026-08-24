# app/parties/services/legal_entity_service.py

"""Сервис юрлиц."""

from __future__ import annotations

from app.parties.models import LegalEntity
from app.parties.repository import LegalEntityRepository


class LegalEntityService:
    def __init__(self, repo: LegalEntityRepository) -> None:
        self._repo = repo

    async def get_by_id(self, id: int) -> LegalEntity | None:
        return await self._repo.get_by_id(id)

    async def list_all(self) -> list[LegalEntity]:
        return await self._repo.list_all()

    async def create(self, **kwargs) -> LegalEntity:
        return await self._repo.create(**kwargs)

    async def update(self, id: int, **kwargs) -> LegalEntity | None:
        return await self._repo.update(id, **kwargs)

    async def soft_delete(self, id: int, user_id: int | None = None) -> bool:
        return await self._repo.soft_delete(id, user_id)
