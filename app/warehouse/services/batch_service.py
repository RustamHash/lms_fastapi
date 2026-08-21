"""Сервис партий."""

from __future__ import annotations

from datetime import date

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.warehouse.models import Batch


class BatchService:
    def __init__(self, session: AsyncSession) -> None:
        self._s = session

    async def create(
        self,
        *,
        product_id: int,
        batch_number: str | None = None,
        production_date: date | None = None,
        expiration_date: date | None = None,
        user_id: int | None = None,
    ) -> Batch:
        if not batch_number:
            batch_number = date.today().strftime("%Y%m%d")

        stmt = select(Batch).where(
            Batch.product_id == product_id,
            Batch.batch_number == batch_number,
        )
        existing = await self._s.scalar(stmt)
        if existing:
            raise ValueError(f"Партия {batch_number} уже существует")

        batch = Batch(
            product_id=product_id,
            batch_number=batch_number,
            production_date=production_date,
            expiration_date=expiration_date,
            created_by_id=user_id,
            updated_by_id=user_id,
        )
        self._s.add(batch)
        await self._s.flush()
        return batch

    async def get_or_create(
        self,
        product_id: int,
        batch_number: str | None = None,
        user_id: int | None = None,
    ) -> tuple[Batch, bool]:
        if not batch_number:
            batch_number = date.today().strftime("%Y%m%d")

        stmt = select(Batch).where(
            Batch.product_id == product_id,
            Batch.batch_number == batch_number,
        )
        batch = await self._s.scalar(stmt)
        if batch:
            return batch, False

        batch = await self.create(
            product_id=product_id,
            batch_number=batch_number,
            user_id=user_id,
        )
        return batch, True

    async def get_by_id(self, batch_id: int) -> Batch | None:
        return await self._s.get(Batch, batch_id)

    async def list_by_product(self, product_id: int) -> list[Batch]:
        stmt = select(Batch).where(
            Batch.product_id == product_id,
        )
        return list(await self._s.scalars(stmt))
