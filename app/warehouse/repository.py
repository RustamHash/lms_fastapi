# app/warehouse/repository.py

"""Репозитории для модуля warehouse."""

from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.infrastructure.repo_base import BaseRepository
from app.warehouse.models import (
    Batch,
    LPN,
    Location,
    Package,
    Product,
    ProductGroup,
    ProductLocation,
    Row,
    StockBalance,
    StockMovement,
    Task,
    TaskLine,
    VirtualWarehouse,
    Warehouse,
    Zone,
)


class ProductRepository(BaseRepository[Product]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, Product)

    async def list_by_depositor(self, depositor_id: int) -> list[Product]:
        stmt = select(Product).where(Product.depositor_id == depositor_id)
        return list(await self._s.scalars(stmt))

    async def get_by_external_id(
        self, depositor_id: int, external_id: str
    ) -> Product | None:
        stmt = select(Product).where(
            Product.depositor_id == depositor_id, Product.external_id == external_id
        )
        return await self._s.scalar(stmt)


class BatchRepository(BaseRepository[Batch]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, Batch)

    async def list_by_product(self, product_id: int) -> list[Batch]:
        stmt = select(Batch).where(Batch.product_id == product_id)
        return list(await self._s.scalars(stmt))

    async def get_by_number(self, product_id: int, batch_number: str) -> Batch | None:
        stmt = select(Batch).where(
            Batch.product_id == product_id, Batch.batch_number == batch_number
        )
        return await self._s.scalar(stmt)


class LPNRepository(BaseRepository[LPN]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, LPN)

    async def get_by_number(self, number: str) -> LPN | None:
        stmt = select(LPN).where(LPN.number == number)
        return await self._s.scalar(stmt)


class StockRepository(BaseRepository[StockBalance]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, StockBalance)

    async def get_balance(
        self,
        product_id: int,
        location_id: int,
        lpn_id: int | None = None,
        batch_id: int | None = None,
        for_update: bool = False,
    ) -> StockBalance | None:
        stmt = select(StockBalance).where(
            StockBalance.product_id == product_id,
            StockBalance.location_id == location_id,
            StockBalance.lpn_id == lpn_id,
            StockBalance.batch_id == batch_id,
        )
        if for_update:
            stmt = stmt.with_for_update()
        return await self._s.scalar(stmt)

    async def create_movement(self, **kwargs) -> StockMovement:
        row = StockMovement(**kwargs)
        self._s.add(row)
        await self._s.flush()
        return row

    async def list_movements(
        self, product_id: int | None = None
    ) -> list[StockMovement]:
        stmt = select(StockMovement)
        if product_id:
            stmt = stmt.where(StockMovement.product_id == product_id)
        return list(await self._s.scalars(stmt))


class TaskRepository(BaseRepository[Task]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, Task)


class TaskLineRepository(BaseRepository[TaskLine]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, TaskLine)

    async def list_by_task(self, task_id: int) -> list[TaskLine]:
        stmt = select(TaskLine).where(TaskLine.task_id == task_id)
        return list(await self._s.scalars(stmt))


class WarehouseRepository(BaseRepository[Warehouse]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, Warehouse)


class VirtualWarehouseRepository(BaseRepository[VirtualWarehouse]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, VirtualWarehouse)


class ZoneRepository(BaseRepository[Zone]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, Zone)


class RowRepository(BaseRepository[Row]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, Row)


class LocationRepository(BaseRepository[Location]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, Location)


class ProductGroupRepository(BaseRepository[ProductGroup]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, ProductGroup)


class PackageRepository(BaseRepository[Package]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, Package)


class ProductLocationRepository(BaseRepository[ProductLocation]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, ProductLocation)
