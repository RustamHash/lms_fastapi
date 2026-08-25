"""Тонкие сервисы топологии склада."""

from __future__ import annotations

from typing import Generic, TypeVar

from app.infrastructure.repo_base import BaseRepository
from app.warehouse.models import Location, Row, VirtualWarehouse, Warehouse, Zone
from app.warehouse.repository import (
    LocationRepository,
    RowRepository,
    VirtualWarehouseRepository,
    WarehouseRepository,
    ZoneRepository,
)

T = TypeVar("T")


class _CrudService(Generic[T]):
    def __init__(self, repo: BaseRepository[T]) -> None:
        self._repo = repo

    async def get_by_id(self, id: int) -> T | None:
        return await self._repo.get_by_id(id)

    async def list_all(self) -> list[T]:
        return await self._repo.list_all()

    async def create(self, **kwargs) -> T:
        return await self._repo.create(**kwargs)

    async def update(self, id: int, **kwargs) -> T | None:
        return await self._repo.update(id, **kwargs)

    async def soft_delete(self, id: int, user_id: int | None = None) -> bool:
        return await self._repo.soft_delete(id, user_id)


class WarehouseService(_CrudService[Warehouse]):
    def __init__(self, repo: WarehouseRepository) -> None:
        super().__init__(repo)


class VirtualWarehouseService(_CrudService[VirtualWarehouse]):
    def __init__(self, repo: VirtualWarehouseRepository) -> None:
        super().__init__(repo)
        self._vw = repo

    async def get_by_depositor_code(
        self, depositor_id: int, code: str
    ) -> VirtualWarehouse | None:
        return await self._vw.get_by_depositor_code(depositor_id, code)


class ZoneService(_CrudService[Zone]):
    def __init__(self, repo: ZoneRepository) -> None:
        super().__init__(repo)


class RowService(_CrudService[Row]):
    def __init__(self, repo: RowRepository) -> None:
        super().__init__(repo)


class LocationService(_CrudService[Location]):
    def __init__(self, repo: LocationRepository) -> None:
        super().__init__(repo)
