"""Сервис упаковок."""

from __future__ import annotations

from app.warehouse.models import Package
from app.warehouse.repository import PackageRepository


class PackageService:
    def __init__(self, repo: PackageRepository) -> None:
        self._repo = repo

    async def get_by_id(self, package_id: int) -> Package | None:
        return await self._repo.get_by_id(package_id)

    async def list_all(self) -> list[Package]:
        return await self._repo.list_all()

    async def create(self, **kwargs) -> Package:
        return await self._repo.create(**kwargs)

    async def update(self, package_id: int, **kwargs) -> Package | None:
        return await self._repo.update(package_id, **kwargs)

    async def soft_delete(self, package_id: int, user_id: int | None = None) -> bool:
        return await self._repo.soft_delete(package_id, user_id)
