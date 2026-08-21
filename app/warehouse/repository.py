"""Репозитории для модуля warehouse."""

from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.warehouse.models import (
    Batch,
    LPN,
    Location,
    Package,
    Product,
    ProductGroup,
    ProductLocation,
    StockBalance,
    StockMovement,
    Task,
    TaskLine,
    VirtualWarehouse,
    Warehouse,
    Zone,
    Row,
)


class ProductRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._s = session

    async def get_by_id(self, product_id: int) -> Product | None:
        return await self._s.get(Product, product_id)

    async def get_by_external_id(self, depositor_id: int, external_id: str) -> Product | None:
        stmt = select(Product).where(
            Product.depositor_id == depositor_id,
            Product.external_id == external_id,
        )
        return await self._s.scalar(stmt)

    async def list_by_depositor(self, depositor_id: int) -> list[Product]:
        stmt = select(Product).where(Product.depositor_id == depositor_id)
        return list(await self._s.scalars(stmt))

    async def list_all(self) -> list[Product]:
        stmt = select(Product)
        return list(await self._s.scalars(stmt))

    async def create(self, **kwargs) -> Product:
        product = Product(**kwargs)
        self._s.add(product)
        await self._s.flush()
        return product

    async def update(self, product_id: int, **kwargs) -> Product | None:
        product = await self.get_by_id(product_id)
        if product is None:
            return None
        for field, value in kwargs.items():
            setattr(product, field, value)
        await self._s.flush()
        return product

    async def delete(self, product_id: int) -> bool:
        product = await self.get_by_id(product_id)
        if product is None:
            return False
        await self._s.delete(product)
        await self._s.flush()
        return True


class BatchRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._s = session

    async def get_by_id(self, batch_id: int) -> Batch | None:
        return await self._s.get(Batch, batch_id)

    async def get_by_number(self, product_id: int, batch_number: str) -> Batch | None:
        stmt = select(Batch).where(
            Batch.product_id == product_id,
            Batch.batch_number == batch_number,
        )
        return await self._s.scalar(stmt)

    async def list_by_product(self, product_id: int) -> list[Batch]:
        stmt = select(Batch).where(Batch.product_id == product_id)
        return list(await self._s.scalars(stmt))

    async def list_all(self) -> list[Batch]:
        stmt = select(Batch)
        return list(await self._s.scalars(stmt))

    async def create(self, **kwargs) -> Batch:
        batch = Batch(**kwargs)
        self._s.add(batch)
        await self._s.flush()
        return batch

    async def update(self, batch_id: int, **kwargs) -> Batch | None:
        batch = await self.get_by_id(batch_id)
        if batch is None:
            return None
        for field, value in kwargs.items():
            setattr(batch, field, value)
        await self._s.flush()
        return batch

    async def delete(self, batch_id: int) -> bool:
        batch = await self.get_by_id(batch_id)
        if batch is None:
            return False
        await self._s.delete(batch)
        await self._s.flush()
        return True


class LPNRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._s = session

    async def get_by_id(self, lpn_id: int) -> LPN | None:
        return await self._s.get(LPN, lpn_id)

    async def get_by_number(self, number: str) -> LPN | None:
        stmt = select(LPN).where(LPN.number == number)
        return await self._s.scalar(stmt)

    async def list_all(self) -> list[LPN]:
        stmt = select(LPN)
        return list(await self._s.scalars(stmt))

    async def create(self, **kwargs) -> LPN:
        lpn = LPN(**kwargs)
        self._s.add(lpn)
        await self._s.flush()
        return lpn

    async def update(self, lpn_id: int, **kwargs) -> LPN | None:
        lpn = await self.get_by_id(lpn_id)
        if lpn is None:
            return None
        for field, value in kwargs.items():
            setattr(lpn, field, value)
        await self._s.flush()
        return lpn

    async def delete(self, lpn_id: int) -> bool:
        lpn = await self.get_by_id(lpn_id)
        if lpn is None:
            return False
        await self._s.delete(lpn)
        await self._s.flush()
        return True


class StockRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._s = session

    async def get_balance_by_id(self, balance_id: int) -> StockBalance | None:
        return await self._s.get(StockBalance, balance_id)

    async def get_balance(
        self,
        product_id: int,
        location_id: int,
        lpn_id: int | None = None,
        batch_id: int | None = None,
    ) -> StockBalance | None:
        stmt = select(StockBalance).where(
            StockBalance.product_id == product_id,
            StockBalance.location_id == location_id,
            StockBalance.lpn_id == lpn_id,
            StockBalance.batch_id == batch_id,
        )
        return await self._s.scalar(stmt)

    async def list_balances(self) -> list[StockBalance]:
        stmt = select(StockBalance)
        return list(await self._s.scalars(stmt))

    async def create_balance(self, **kwargs) -> StockBalance:
        balance = StockBalance(**kwargs)
        self._s.add(balance)
        await self._s.flush()
        return balance

    async def create_movement(self, **kwargs) -> StockMovement:
        movement = StockMovement(**kwargs)
        self._s.add(movement)
        await self._s.flush()
        return movement

    async def get_movement_by_id(self, movement_id: int) -> StockMovement | None:
        return await self._s.get(StockMovement, movement_id)

    async def list_movements(self, product_id: int | None = None) -> list[StockMovement]:
        stmt = select(StockMovement)
        if product_id:
            stmt = stmt.where(StockMovement.product_id == product_id)
        return list(await self._s.scalars(stmt))


class TaskRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._s = session

    async def get_by_id(self, task_id: int) -> Task | None:
        return await self._s.get(Task, task_id)

    async def list_all(self) -> list[Task]:
        stmt = select(Task)
        return list(await self._s.scalars(stmt))

    async def create(self, **kwargs) -> Task:
        task = Task(**kwargs)
        self._s.add(task)
        await self._s.flush()
        return task

    async def update(self, task_id: int, **kwargs) -> Task | None:
        task = await self.get_by_id(task_id)
        if task is None:
            return None
        for field, value in kwargs.items():
            setattr(task, field, value)
        await self._s.flush()
        return task

    async def delete(self, task_id: int) -> bool:
        task = await self.get_by_id(task_id)
        if task is None:
            return False
        await self._s.delete(task)
        await self._s.flush()
        return True


class TaskLineRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._s = session

    async def get_by_id(self, line_id: int) -> TaskLine | None:
        return await self._s.get(TaskLine, line_id)

    async def list_by_task(self, task_id: int) -> list[TaskLine]:
        stmt = select(TaskLine).where(TaskLine.task_id == task_id)
        return list(await self._s.scalars(stmt))

    async def create(self, **kwargs) -> TaskLine:
        line = TaskLine(**kwargs)
        self._s.add(line)
        await self._s.flush()
        return line

    async def update(self, line_id: int, **kwargs) -> TaskLine | None:
        line = await self.get_by_id(line_id)
        if line is None:
            return None
        for field, value in kwargs.items():
            setattr(line, field, value)
        await self._s.flush()
        return line


class WarehouseRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._s = session

    async def get_by_id(self, warehouse_id: int) -> Warehouse | None:
        return await self._s.get(Warehouse, warehouse_id)

    async def list_all(self) -> list[Warehouse]:
        return list(await self._s.scalars(select(Warehouse)))

    async def create(self, **kwargs) -> Warehouse:
        wh = Warehouse(**kwargs)
        self._s.add(wh)
        await self._s.flush()
        return wh

    async def update(self, warehouse_id: int, **kwargs) -> Warehouse | None:
        wh = await self.get_by_id(warehouse_id)
        if wh is None:
            return None
        for field, value in kwargs.items():
            setattr(wh, field, value)
        await self._s.flush()
        return wh

    async def delete(self, warehouse_id: int) -> bool:
        wh = await self.get_by_id(warehouse_id)
        if wh is None:
            return False
        await self._s.delete(wh)
        await self._s.flush()
        return True


class VirtualWarehouseRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._s = session

    async def get_by_id(self, vw_id: int) -> VirtualWarehouse | None:
        return await self._s.get(VirtualWarehouse, vw_id)

    async def list_all(self) -> list[VirtualWarehouse]:
        return list(await self._s.scalars(select(VirtualWarehouse)))

    async def create(self, **kwargs) -> VirtualWarehouse:
        vw = VirtualWarehouse(**kwargs)
        self._s.add(vw)
        await self._s.flush()
        return vw

    async def update(self, vw_id: int, **kwargs) -> VirtualWarehouse | None:
        vw = await self.get_by_id(vw_id)
        if vw is None:
            return None
        for field, value in kwargs.items():
            setattr(vw, field, value)
        await self._s.flush()
        return vw

    async def delete(self, vw_id: int) -> bool:
        vw = await self.get_by_id(vw_id)
        if vw is None:
            return False
        await self._s.delete(vw)
        await self._s.flush()
        return True


class ZoneRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._s = session

    async def get_by_id(self, zone_id: int) -> Zone | None:
        return await self._s.get(Zone, zone_id)

    async def list_all(self) -> list[Zone]:
        return list(await self._s.scalars(select(Zone)))

    async def create(self, **kwargs) -> Zone:
        zone = Zone(**kwargs)
        self._s.add(zone)
        await self._s.flush()
        return zone

    async def update(self, zone_id: int, **kwargs) -> Zone | None:
        zone = await self.get_by_id(zone_id)
        if zone is None:
            return None
        for field, value in kwargs.items():
            setattr(zone, field, value)
        await self._s.flush()
        return zone

    async def delete(self, zone_id: int) -> bool:
        zone = await self.get_by_id(zone_id)
        if zone is None:
            return False
        await self._s.delete(zone)
        await self._s.flush()
        return True


class RowRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._s = session

    async def get_by_id(self, row_id: int) -> Row | None:
        return await self._s.get(Row, row_id)

    async def list_all(self) -> list[Row]:
        return list(await self._s.scalars(select(Row)))

    async def create(self, **kwargs) -> Row:
        row = Row(**kwargs)
        self._s.add(row)
        await self._s.flush()
        return row

    async def update(self, row_id: int, **kwargs) -> Row | None:
        row = await self.get_by_id(row_id)
        if row is None:
            return None
        for field, value in kwargs.items():
            setattr(row, field, value)
        await self._s.flush()
        return row

    async def delete(self, row_id: int) -> bool:
        row = await self.get_by_id(row_id)
        if row is None:
            return False
        await self._s.delete(row)
        await self._s.flush()
        return True


class LocationRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._s = session

    async def get_by_id(self, location_id: int) -> Location | None:
        return await self._s.get(Location, location_id)

    async def list_all(self) -> list[Location]:
        return list(await self._s.scalars(select(Location)))

    async def create(self, **kwargs) -> Location:
        loc = Location(**kwargs)
        self._s.add(loc)
        await self._s.flush()
        return loc

    async def update(self, location_id: int, **kwargs) -> Location | None:
        loc = await self.get_by_id(location_id)
        if loc is None:
            return None
        for field, value in kwargs.items():
            setattr(loc, field, value)
        await self._s.flush()
        return loc

    async def delete(self, location_id: int) -> bool:
        loc = await self.get_by_id(location_id)
        if loc is None:
            return False
        await self._s.delete(loc)
        await self._s.flush()
        return True


class ProductGroupRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._s = session

    async def get_by_id(self, group_id: int) -> ProductGroup | None:
        return await self._s.get(ProductGroup, group_id)

    async def get_by_name(self, name: str) -> ProductGroup | None:
        stmt = select(ProductGroup).where(ProductGroup.name == name)
        return await self._s.scalar(stmt)

    async def list_all(self) -> list[ProductGroup]:
        return list(await self._s.scalars(select(ProductGroup)))

    async def create(self, **kwargs) -> ProductGroup:
        group = ProductGroup(**kwargs)
        self._s.add(group)
        await self._s.flush()
        return group

    async def update(self, group_id: int, **kwargs) -> ProductGroup | None:
        group = await self.get_by_id(group_id)
        if group is None:
            return None
        for field, value in kwargs.items():
            setattr(group, field, value)
        await self._s.flush()
        return group

    async def delete(self, group_id: int) -> bool:
        group = await self.get_by_id(group_id)
        if group is None:
            return False
        await self._s.delete(group)
        await self._s.flush()
        return True


class PackageRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._s = session

    async def get_by_id(self, package_id: int) -> Package | None:
        return await self._s.get(Package, package_id)

    async def list_all(self) -> list[Package]:
        return list(await self._s.scalars(select(Package)))

    async def create(self, **kwargs) -> Package:
        package = Package(**kwargs)
        self._s.add(package)
        await self._s.flush()
        return package

    async def update(self, package_id: int, **kwargs) -> Package | None:
        package = await self.get_by_id(package_id)
        if package is None:
            return None
        for field, value in kwargs.items():
            setattr(package, field, value)
        await self._s.flush()
        return package

    async def delete(self, package_id: int) -> bool:
        package = await self.get_by_id(package_id)
        if package is None:
            return False
        await self._s.delete(package)
        await self._s.flush()
        return True


class ProductLocationRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._s = session

    async def get_by_id(self, pl_id: int) -> ProductLocation | None:
        return await self._s.get(ProductLocation, pl_id)

    async def list_all(self) -> list[ProductLocation]:
        return list(await self._s.scalars(select(ProductLocation)))

    async def create(self, **kwargs) -> ProductLocation:
        pl = ProductLocation(**kwargs)
        self._s.add(pl)
        await self._s.flush()
        return pl

    async def update(self, pl_id: int, **kwargs) -> ProductLocation | None:
        pl = await self.get_by_id(pl_id)
        if pl is None:
            return None
        for field, value in kwargs.items():
            setattr(pl, field, value)
        await self._s.flush()
        return pl

    async def delete(self, pl_id: int) -> bool:
        pl = await self.get_by_id(pl_id)
        if pl is None:
            return False
        await self._s.delete(pl)
        await self._s.flush()
        return True
