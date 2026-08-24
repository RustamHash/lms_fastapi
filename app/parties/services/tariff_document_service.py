# app/parties/services/tariff_document_service.py

"""Сервис тарифных документов."""

from __future__ import annotations

from app.parties.models import TariffDocument
from app.parties.repository import TariffDocumentRepository


class TariffDocumentService:
    def __init__(self, repo: TariffDocumentRepository) -> None:
        self._repo = repo

    async def get_by_id(self, id: int) -> TariffDocument | None:
        return await self._repo.get_by_id(id)

    async def list_all(self) -> list[TariffDocument]:
        return await self._repo.list_all()

    async def create(self, **kwargs) -> TariffDocument:
        return await self._repo.create(**kwargs)

    async def update(self, id: int, **kwargs) -> TariffDocument | None:
        return await self._repo.update(id, **kwargs)

    async def soft_delete(self, id: int, user_id: int | None = None) -> bool:
        return await self._repo.soft_delete(id, user_id)
