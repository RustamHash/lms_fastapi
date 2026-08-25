# app/warehouse/repository.py

"""Репозитории для модуля warehouse."""

from __future__ import annotations

from decimal import Decimal

from sqlalchemy import func, select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from app.infrastructure.repo_base import BaseRepository
from app.core.statuses import TaskStatus
from app.warehouse.models import (
    Batch,
    LPN,
    Location,
    Package,
    Product,
    ProductGroup,
    ProductLocation,
    ReceivingDiscrepancy,
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
        return (await self._s.scalars(stmt)).first()


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
        lpn_id: int,
        batch_id: int,
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
        return (await self._s.scalars(stmt)).first()

    async def sum_available(
        self,
        product_id: int,
        location_id: int | None = None,
        lpn_id: int | None = None,
        batch_id: int | None = None,
    ) -> Decimal:
        stmt = select(
            func.coalesce(
                func.sum(StockBalance.quantity - StockBalance.reserved_quantity),
                0,
            )
        ).where(StockBalance.product_id == product_id)
        if location_id is not None:
            stmt = stmt.where(StockBalance.location_id == location_id)
        if lpn_id is not None:
            stmt = stmt.where(StockBalance.lpn_id == lpn_id)
        if batch_id is not None:
            stmt = stmt.where(StockBalance.batch_id == batch_id)
        value = await self._s.scalar(stmt)
        return Decimal(value) if value is not None else Decimal("0")

    async def create_movement(self, **kwargs) -> StockMovement:
        row = StockMovement(**kwargs)
        self._s.add(row)
        await self._s.flush()
        return row

    async def get_movement(self, movement_id: int) -> StockMovement | None:
        return await self._s.get(StockMovement, movement_id)

    async def list_available_fefo(self, product_id: int, warehouse_id: int) -> list[StockBalance]:
        stmt = (
            select(StockBalance)
            .join(Batch, StockBalance.batch_id == Batch.id)
            .join(Location, StockBalance.location_id == Location.id)
            .join(Row, Location.row_id == Row.id)
            .join(Zone, Row.zone_id == Zone.id)
            .where(
                StockBalance.product_id == product_id,
                StockBalance.is_deleted.is_(False),
                Zone.warehouse_id == warehouse_id,
                (StockBalance.quantity - StockBalance.reserved_quantity) > 0,
            )
            .order_by(Batch.expiration_date.asc().nulls_last(), StockBalance.id.asc())
        )
        return list(await self._s.scalars(stmt))

    async def list_movements(
        self, product_id: int | None = None
    ) -> list[StockMovement]:
        stmt = select(StockMovement)
        if product_id:
            stmt = stmt.where(StockMovement.product_id == product_id)
        return list(await self._s.scalars(stmt))

    async def list_movements_for_inbound(
        self, inbound_order_id: int
    ) -> list[StockMovement]:
        stmt = (
            select(StockMovement)
            .join(TaskLine, StockMovement.task_line_id == TaskLine.id)
            .join(Task, TaskLine.task_id == Task.id)
            .options(
                selectinload(StockMovement.product),
                selectinload(StockMovement.batch),
                selectinload(StockMovement.lpn),
                selectinload(StockMovement.location),
            )
            .where(
                Task.inbound_order_id == inbound_order_id,
                Task.task_type == "receiving",
                Task.is_deleted.is_(False),
            )
            .order_by(StockMovement.moved_at.asc(), StockMovement.id.asc())
        )
        return list((await self._s.scalars(stmt)).unique().all())

    async def list_movements_for_outbound(
        self, outbound_order_id: int
    ) -> list[StockMovement]:
        stmt = (
            select(StockMovement)
            .join(TaskLine, StockMovement.task_line_id == TaskLine.id)
            .join(Task, TaskLine.task_id == Task.id)
            .options(
                selectinload(StockMovement.product),
                selectinload(StockMovement.batch),
                selectinload(StockMovement.lpn),
                selectinload(StockMovement.location),
            )
            .where(
                Task.outbound_order_id == outbound_order_id,
                Task.task_type == "picking",
                Task.is_deleted.is_(False),
            )
            .order_by(StockMovement.moved_at.asc(), StockMovement.id.asc())
        )
        return list((await self._s.scalars(stmt)).unique().all())

    async def list_movements_for_document(
        self, document_id: int
    ) -> list[StockMovement]:
        stmt = (
            select(StockMovement)
            .options(
                selectinload(StockMovement.product),
                selectinload(StockMovement.batch),
                selectinload(StockMovement.lpn),
                selectinload(StockMovement.location),
            )
            .where(StockMovement.document_id == document_id)
            .order_by(StockMovement.moved_at.asc(), StockMovement.id.asc())
        )
        return list(await self._s.scalars(stmt))


class TaskRepository(BaseRepository[Task]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, Task)

    async def get_active_for_inbound(self, inbound_order_id: int) -> Task | None:
        stmt = select(Task).where(
            Task.inbound_order_id == inbound_order_id,
            Task.task_type == "receiving",
            Task.is_deleted.is_(False),
            Task.status.notin_([TaskStatus.CANCELLED.value]),
        )
        return (await self._s.scalars(stmt)).first()

    async def get_active_for_outbound(self, outbound_order_id: int) -> Task | None:
        stmt = select(Task).where(
            Task.outbound_order_id == outbound_order_id,
            Task.task_type == "picking",
            Task.is_deleted.is_(False),
            Task.status.notin_([TaskStatus.CANCELLED.value]),
        )
        return (await self._s.scalars(stmt)).first()


class TaskLineRepository(BaseRepository[TaskLine]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, TaskLine)

    async def list_by_task(self, task_id: int) -> list[TaskLine]:
        stmt = select(TaskLine).where(
            TaskLine.task_id == task_id,
            TaskLine.is_deleted.is_(False),
        )
        return list(await self._s.scalars(stmt))

    async def list_for_inbound(self, inbound_order_id: int) -> list[TaskLine]:
        stmt = (
            select(TaskLine)
            .join(Task, TaskLine.task_id == Task.id)
            .options(
                selectinload(TaskLine.product),
                selectinload(TaskLine.batch),
            )
            .where(
                Task.inbound_order_id == inbound_order_id,
                Task.task_type == "receiving",
                Task.is_deleted.is_(False),
                TaskLine.is_deleted.is_(False),
            )
        )
        return list((await self._s.scalars(stmt)).unique().all())

    async def list_for_outbound(self, outbound_order_id: int) -> list[TaskLine]:
        stmt = (
            select(TaskLine)
            .join(Task, TaskLine.task_id == Task.id)
            .options(
                selectinload(TaskLine.product),
                selectinload(TaskLine.batch),
            )
            .where(
                Task.outbound_order_id == outbound_order_id,
                Task.task_type == "picking",
                Task.is_deleted.is_(False),
                TaskLine.is_deleted.is_(False),
            )
        )
        return list((await self._s.scalars(stmt)).unique().all())


class WarehouseRepository(BaseRepository[Warehouse]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, Warehouse)


class VirtualWarehouseRepository(BaseRepository[VirtualWarehouse]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, VirtualWarehouse)

    async def get_by_depositor_code(
        self, depositor_id: int, code: str
    ) -> VirtualWarehouse | None:
        stmt = select(VirtualWarehouse).where(
            VirtualWarehouse.depositor_id == depositor_id,
            VirtualWarehouse.code == code,
        )
        return await self._s.scalar(stmt)


class ZoneRepository(BaseRepository[Zone]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, Zone)


class RowRepository(BaseRepository[Row]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, Row)


class LocationRepository(BaseRepository[Location]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, Location)

    async def belongs_to_warehouse(self, location_id: int, warehouse_id: int) -> bool:
        stmt = (
            select(Location.id)
            .join(Row, Location.row_id == Row.id)
            .join(Zone, Row.zone_id == Zone.id)
            .where(Location.id == location_id, Zone.warehouse_id == warehouse_id)
        )
        return (await self._s.scalar(stmt)) is not None


class ReceivingDiscrepancyRepository(BaseRepository[ReceivingDiscrepancy]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, ReceivingDiscrepancy)

    async def list_by_line(self, task_line_id: int) -> list[ReceivingDiscrepancy]:
        stmt = select(ReceivingDiscrepancy).where(
            ReceivingDiscrepancy.task_line_id == task_line_id
        )
        return list(await self._s.scalars(stmt))


class ProductGroupRepository(BaseRepository[ProductGroup]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, ProductGroup)

    async def get_by_name(self, name: str) -> ProductGroup | None:
        stmt = select(self._model).where(self._model.name == name)
        return (await self._s.scalars(stmt)).first()


class PackageRepository(BaseRepository[Package]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, Package)


class ProductLocationRepository(BaseRepository[ProductLocation]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, ProductLocation)
