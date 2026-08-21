"""Сервис тарифов."""

from __future__ import annotations

from decimal import Decimal

from app.parties.models import Tariff, TariffDocument
from app.parties.repository import TariffRepository


class TariffService:
    def __init__(self, repo: TariffRepository) -> None:
        self._repo = repo

    async def create_document(self, user_id: int | None, **kwargs) -> TariffDocument:
        if not kwargs.get("contract_id"):
            raise ValueError("Договор обязателен")
        if not kwargs.get("number"):
            raise ValueError("Номер обязателен")

        return await self._repo.insert_document(
            **kwargs,
        )

    async def create_tariff(self, user_id: int | None, **kwargs) -> Tariff:
        if not kwargs.get("document_id"):
            raise ValueError("Тарифный документ обязателен")
        if not kwargs.get("name"):
            raise ValueError("Название обязательно")
        if kwargs.get("price") is None or kwargs["price"] < 0:
            raise ValueError("Цена обязательна и не может быть отрицательной")

        return await self._repo.insert_tariff(
            **kwargs,
        )

    async def get_document(self, document_id: int) -> TariffDocument | None:
        return await self._repo.get_document_by_id(document_id)

    async def list_tariffs(self, document_id: int) -> list[Tariff]:
        return await self._repo.list_tariffs_by_document(document_id)
