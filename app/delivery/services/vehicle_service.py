"""Сервис автомобилей."""

from __future__ import annotations

from app.delivery.models import Vehicle
from app.delivery.repository import VehicleRepository


class VehicleService:
    def __init__(self, repo: VehicleRepository) -> None:
        self._repo = repo

    async def get_by_id(self, vehicle_id: int) -> Vehicle | None:
        return await self._repo.get_by_id(vehicle_id)

    async def list_all(self) -> list[Vehicle]:
        return await self._repo.list_all()

    async def create(self, *, user_id: int | None = None, **kwargs) -> Vehicle:
        return await self._repo.create(**kwargs)

    async def update(self, vehicle_id: int, user_id: int | None = None, **kwargs) -> Vehicle | None:
        return await self._repo.update(vehicle_id, **kwargs)

    async def soft_delete(self, vehicle_id: int, user_id: int | None = None) -> bool:
        return await self._repo.soft_delete(vehicle_id, user_id)
