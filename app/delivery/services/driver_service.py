"""Сервис водителей."""

from __future__ import annotations

from app.delivery.models import Driver
from app.delivery.repository import DriverRepository


class DriverService:
    def __init__(self, repo: DriverRepository) -> None:
        self._repo = repo

    async def get_by_id(self, driver_id: int) -> Driver | None:
        return await self._repo.get_by_id(driver_id)

    async def list_all(self) -> list[Driver]:
        return await self._repo.list_all()

    async def create(self, *, user_id: int | None = None, **kwargs) -> Driver:
        return await self._repo.create(**kwargs)

    async def update(self, driver_id: int, user_id: int | None = None, **kwargs) -> Driver | None:
        return await self._repo.update(driver_id, **kwargs)

    async def soft_delete(self, driver_id: int, user_id: int | None = None) -> bool:
        return await self._repo.soft_delete(driver_id, user_id)
