# app/delivery/repository.py

"""Репозитории для модуля delivery."""

from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.delivery.models import DeliveryDeviation, DeliveryOrder, Driver, Route, RouteLine, Vehicle


class DeliveryOrderRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._s = session

    async def get_by_id(self, id: int) -> DeliveryOrder | None:
        stmt = select(DeliveryOrder).where(DeliveryOrder.id == id).options(selectinload(DeliveryOrder.outbound_order), selectinload(DeliveryOrder.document), selectinload(DeliveryOrder.deviations))
        return await self._s.scalar(stmt)

    async def list_all(self) -> list[DeliveryOrder]:
        stmt = select(DeliveryOrder).options(selectinload(DeliveryOrder.outbound_order))
        return list(await self._s.scalars(stmt))

    async def create(self, **kwargs) -> DeliveryOrder:
        row = DeliveryOrder(**kwargs)
        self._s.add(row)
        await self._s.flush()
        return row

    async def update(self, id: int, **kwargs) -> DeliveryOrder | None:
        row = await self._s.get(DeliveryOrder, id)
        if row is None:
            return None
        for field, value in kwargs.items():
            setattr(row, field, value)
        await self._s.flush()
        return row

    async def soft_delete(self, id: int, user_id: int | None = None) -> bool:
        row = await self._s.get(DeliveryOrder, id)
        if row is None:
            return False
        row.soft_delete(user_id)
        await self._s.flush()
        return True


class DriverRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._s = session

    async def get_by_id(self, id: int) -> Driver | None:
        return await self._s.get(Driver, id)

    async def list_all(self) -> list[Driver]:
        return list(await self._s.scalars(select(Driver)))

    async def create(self, **kwargs) -> Driver:
        row = Driver(**kwargs)
        self._s.add(row)
        await self._s.flush()
        return row

    async def update(self, id: int, **kwargs) -> Driver | None:
        row = await self._s.get(Driver, id)
        if row is None:
            return None
        for field, value in kwargs.items():
            setattr(row, field, value)
        await self._s.flush()
        return row

    async def soft_delete(self, id: int, user_id: int | None = None) -> bool:
        row = await self._s.get(Driver, id)
        if row is None:
            return False
        row.soft_delete(user_id)
        await self._s.flush()
        return True


class VehicleRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._s = session

    async def get_by_id(self, id: int) -> Vehicle | None:
        return await self._s.get(Vehicle, id)

    async def list_all(self) -> list[Vehicle]:
        return list(await self._s.scalars(select(Vehicle)))

    async def create(self, **kwargs) -> Vehicle:
        row = Vehicle(**kwargs)
        self._s.add(row)
        await self._s.flush()
        return row

    async def update(self, id: int, **kwargs) -> Vehicle | None:
        row = await self._s.get(Vehicle, id)
        if row is None:
            return None
        for field, value in kwargs.items():
            setattr(row, field, value)
        await self._s.flush()
        return row

    async def soft_delete(self, id: int, user_id: int | None = None) -> bool:
        row = await self._s.get(Vehicle, id)
        if row is None:
            return False
        row.soft_delete(user_id)
        await self._s.flush()
        return True


class RouteRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._s = session

    async def get_by_id(self, id: int) -> Route | None:
        stmt = select(Route).where(Route.id == id).options(selectinload(Route.driver), selectinload(Route.vehicle), selectinload(Route.lines))
        return await self._s.scalar(stmt)

    async def list_all(self) -> list[Route]:
        stmt = select(Route).options(selectinload(Route.driver), selectinload(Route.vehicle))
        return list(await self._s.scalars(stmt))

    async def create(self, **kwargs) -> Route:
        row = Route(**kwargs)
        self._s.add(row)
        await self._s.flush()
        return row

    async def update(self, id: int, **kwargs) -> Route | None:
        row = await self._s.get(Route, id)
        if row is None:
            return None
        for field, value in kwargs.items():
            setattr(row, field, value)
        await self._s.flush()
        return row

    async def soft_delete(self, id: int, user_id: int | None = None) -> bool:
        row = await self._s.get(Route, id)
        if row is None:
            return False
        row.soft_delete(user_id)
        await self._s.flush()
        return True


class RouteLineRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._s = session

    async def get_by_id(self, id: int) -> RouteLine | None:
        return await self._s.get(RouteLine, id)

    async def list_all(self) -> list[RouteLine]:
        return list(await self._s.scalars(select(RouteLine)))

    async def list_by_route(self, route_id: int) -> list[RouteLine]:
        stmt = select(RouteLine).where(RouteLine.route_id == route_id)
        return list(await self._s.scalars(stmt))

    async def create(self, **kwargs) -> RouteLine:
        row = RouteLine(**kwargs)
        self._s.add(row)
        await self._s.flush()
        return row

    async def update(self, id: int, **kwargs) -> RouteLine | None:
        row = await self._s.get(RouteLine, id)
        if row is None:
            return None
        for field, value in kwargs.items():
            setattr(row, field, value)
        await self._s.flush()
        return row

    async def soft_delete(self, id: int, user_id: int | None = None) -> bool:
        row = await self._s.get(RouteLine, id)
        if row is None:
            return False
        row.soft_delete(user_id)
        await self._s.flush()
        return True


class DeviationRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._s = session

    async def get_by_id(self, id: int) -> DeliveryDeviation | None:
        return await self._s.get(DeliveryDeviation, id)

    async def list_all(self) -> list[DeliveryDeviation]:
        return list(await self._s.scalars(select(DeliveryDeviation)))

    async def list_by_order(self, order_id: int) -> list[DeliveryDeviation]:
        stmt = select(DeliveryDeviation).where(DeliveryDeviation.delivery_order_id == order_id)
        return list(await self._s.scalars(stmt))

    async def create(self, **kwargs) -> DeliveryDeviation:
        row = DeliveryDeviation(**kwargs)
        self._s.add(row)
        await self._s.flush()
        return row

    async def update(self, id: int, **kwargs) -> DeliveryDeviation | None:
        row = await self._s.get(DeliveryDeviation, id)
        if row is None:
            return None
        for field, value in kwargs.items():
            setattr(row, field, value)
        await self._s.flush()
        return row

    async def soft_delete(self, id: int, user_id: int | None = None) -> bool:
        row = await self._s.get(DeliveryDeviation, id)
        if row is None:
            return False
        row.soft_delete(user_id)
        await self._s.flush()
        return True
