"""Сервис связей товар–ячейка."""

from __future__ import annotations

from app.warehouse.models import ProductLocation
from app.warehouse.repository import ProductLocationRepository


class ProductLocationService:
    def __init__(self, repo: ProductLocationRepository) -> None:
        self._repo = repo

    async def get_by_id(self, pl_id: int) -> ProductLocation | None:
        return await self._repo.get_by_id(pl_id)

    async def list_all(self) -> list[ProductLocation]:
        return await self._repo.list_all()

    async def create(self, **kwargs) -> ProductLocation:
        return await self._repo.create(**kwargs)

    async def soft_delete(self, pl_id: int, user_id: int | None = None) -> bool:
        return await self._repo.soft_delete(pl_id, user_id)
