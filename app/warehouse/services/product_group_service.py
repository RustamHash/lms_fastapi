"""Сервис групп товаров."""

from __future__ import annotations

from app.core.exceptions import ConflictError
from app.warehouse.models import ProductGroup
from app.warehouse.repository import ProductGroupRepository


class ProductGroupService:
    def __init__(self, repo: ProductGroupRepository) -> None:
        self._repo = repo

    async def get_by_id(self, group_id: int) -> ProductGroup | None:
        return await self._repo.get_by_id(group_id)

    async def list_all(self) -> list[ProductGroup]:
        return await self._repo.list_all()

    async def create(self, *, name: str) -> ProductGroup:
        existing = await self._repo.get_by_name(name)
        if existing:
            raise ConflictError(f"Группа {name} уже существует")
        return await self._repo.create(name=name)

    async def update(self, group_id: int, **kwargs) -> ProductGroup | None:
        return await self._repo.update(group_id, **kwargs)

    async def soft_delete(self, group_id: int, user_id: int | None = None) -> bool:
        return await self._repo.soft_delete(group_id, user_id)
