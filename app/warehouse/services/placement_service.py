"""Стратегия размещения (FEFO)."""

from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.warehouse.models import Location, ProductLocation, Row, StockBalance, Zone


class PlacementService:
    def __init__(self, session: AsyncSession) -> None:
        self._s = session

    async def find_location(
        self,
        *,
        product_id: int,
        batch_id: int,
        warehouse_id: int,
    ) -> tuple[str, Location | None, int | None]:
        """
        Найти ячейку для размещения.

        Возвращает:
        - ("place", location, None) — разместить сюда
        - ("replace", location, old_batch_id) — заменить старую партию
        - ("none", None, None) — не найдено
        """
        # 1. Закреплённые ячейки отбора
        stmt = (
            select(ProductLocation, Location)
            .join(Location, ProductLocation.location_id == Location.id)
            .where(
                ProductLocation.product_id == product_id,
            )
            .order_by(Location.id)
        )
        picking_locations = await self._s.execute(stmt)

        for pl, location in picking_locations:
            result = await self._check_picking_location(
                product_id=product_id,
                batch_id=batch_id,
                location_id=location.id,
            )
            if result:
                return result

        # 2. Первая свободная ячейка хранения
        storage_location = await self._find_storage_location(warehouse_id)
        if storage_location:
            return ("place", storage_location, None)

        return ("none", None, None)

    async def _check_picking_location(
        self,
        *,
        product_id: int,
        batch_id: int,
        location_id: int,
    ) -> tuple[str, Location | None, int | None] | None:
        stmt = select(StockBalance).where(
            StockBalance.product_id == product_id,
            StockBalance.location_id == location_id,
        )
        balances = list(await self._s.scalars(stmt))

        if not balances:
            location = await self._s.get(Location, location_id)
            return ("place", location, None)

        for balance in balances:
            if balance.batch_id == batch_id:
                location = await self._s.get(Location, location_id)
                return ("place", location, None)
            else:
                if await self._is_fresher(batch_id, balance.batch_id):
                    location = await self._s.get(Location, location_id)
                    return ("replace", location, balance.batch_id)

        return None

    async def _is_fresher(self, new_batch_id: int, old_batch_id: int) -> bool:
        from app.warehouse.models import Batch

        new_batch = await self._s.get(Batch, new_batch_id)
        old_batch = await self._s.get(Batch, old_batch_id)

        if not new_batch or not old_batch:
            return False

        new_exp = new_batch.expiration_date
        old_exp = old_batch.expiration_date

        if not new_exp:
            return False
        if not old_exp:
            return True

        return new_exp < old_exp

    async def _find_storage_location(self, warehouse_id: int) -> Location | None:
        stmt = (
            select(Location)
            .join(Row, Location.row_id == Row.id)
            .join(Zone, Row.zone_id == Zone.id)
            .where(
                Zone.warehouse_id == warehouse_id,
                Zone.zone_type == "storage",
            )
            .order_by(Location.id)
        )
        locations = await self._s.scalars(stmt)

        for location in locations:
            balance_stmt = (
                select(StockBalance.id)
                .where(
                    StockBalance.location_id == location.id,
                    StockBalance.quantity > 0,
                    StockBalance.is_deleted.is_(False),
                )
                .limit(1)
            )
            has_stock = await self._s.scalar(balance_stmt)
            if not has_stock:
                return location

        return None
