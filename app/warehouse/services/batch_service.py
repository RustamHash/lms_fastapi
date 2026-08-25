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
        return await self._repo.list_by_product(product_id)

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
        self,
        product_id: int,
        batch_number: str | None = None,
        user_id: int | None = None,
        production_date: date | None = None,
        expiration_date: date | None = None,
    ) -> tuple[Batch, bool]:
        if not batch_number:
            batch_number = date.today().strftime("%Y%m%d")

        batch = await self._repo.get_by_number(product_id, batch_number)
        if batch:
            updates = {}
            if production_date and not batch.production_date:
                updates["production_date"] = production_date
            if expiration_date and not batch.expiration_date:
                updates["expiration_date"] = expiration_date
            if updates:
                batch = await self._repo.update(batch.id, **updates) or batch
            return batch, False

        batch = await self._repo.create(
            product_id=product_id,
            batch_number=batch_number,
            production_date=production_date,
            expiration_date=expiration_date,
        )
        return batch, True

    async def update(self, batch_id: int, user_id: int | None = None, **kwargs) -> Batch | None:
        return await self._repo.update(batch_id, **kwargs)

    async def soft_delete(self, batch_id: int, user_id: int | None = None) -> bool:
        return await self._repo.soft_delete(batch_id, user_id)
