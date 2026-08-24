"""Сервис партий."""

from __future__ import annotations

from datetime import date

from app.warehouse.models import Batch
from app.warehouse.repository import BatchRepository


class BatchService:
    def __init__(self, repo: BatchRepository) -> None:
        self._repo = repo

    async def get_by_id(self, batch_id: int) -> Batch | None:
        return await self._repo.get_by_id(batch_id)

    async def list_all(self) -> list[Batch]:
        return await self._repo.list_all()

    async def list_by_product(self, product_id: int) -> list[Batch]:
        return await self._repo.list_all()

    async def create(
        self,
        *,
        user_id: int | None = None,
        product_id: int,
        batch_number: str | None = None,
        production_date: date | None = None,
        expiration_date: date | None = None,
    ) -> Batch:
        if not batch_number:
            batch_number = date.today().strftime("%Y%m%d")

        existing = await self._repo.get_by_number(product_id, batch_number)
        if existing:
            raise ValueError(f"Партия {batch_number} уже существует")

        return await self._repo.create(
            product_id=product_id,
            batch_number=batch_number,
            production_date=production_date,
            expiration_date=expiration_date,
        )

    async def get_or_create(
        self, product_id: int, batch_number: str | None = None, user_id: int | None = None
    ) -> tuple[Batch, bool]:
        if not batch_number:
            batch_number = date.today().strftime("%Y%m%d")

        batch = await self._repo.get_by_number(product_id, batch_number)
        if batch:
            return batch, False

        batch = await self.create(user_id=user_id, product_id=product_id, batch_number=batch_number)
        return batch, True

    async def soft_delete(self, batch_id: int, user_id: int | None = None) -> bool:
        return await self._repo.soft_delete(batch_id, user_id)
