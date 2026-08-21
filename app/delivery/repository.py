"""Репозитории для модуля delivery."""

from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.delivery.models import DeliveryDeviation, DeliveryOrder, Driver, Route, RouteLine, Vehicle


class DeliveryOrderRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._s = session

    async def get_by_id(self, order_id: int) -> DeliveryOrder | None:
        return await self._s.get(DeliveryOrder, order_id)

    async def list_all(self) -> list[DeliveryOrder]:
        stmt = select(DeliveryOrder)
        return list(await self._s.scalars(stmt))

    async def create(self, **kwargs) -> DeliveryOrder:
        order = DeliveryOrder(**kwargs)
        self._s.add(order)
        await self._s.flush()
        return order

    async def update(self, order_id: int, **kwargs) -> DeliveryOrder | None:
        order = await self.get_by_id(order_id)
        if order is None:
            return None
        for field, value in kwargs.items():
            setattr(order, field, value)
        await self._s.flush()
        return order

    async def delete(self, order_id: int) -> bool:
        order = await self.get_by_id(order_id)
        if order is None:
            return False
        await self._s.delete(order)
        await self._s.flush()
        return True


class DriverRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._s = session

    async def get_by_id(self, driver_id: int) -> Driver | None:
        return await self._s.get(Driver, driver_id)

    async def list_all(self) -> list[Driver]:
        stmt = select(Driver)
        return list(await self._s.scalars(stmt))

    async def create(self, **kwargs) -> Driver:
        driver = Driver(**kwargs)
        self._s.add(driver)
        await self._s.flush()
        return driver

    async def update(self, driver_id: int, **kwargs) -> Driver | None:
        driver = await self.get_by_id(driver_id)
        if driver is None:
            return None
        for field, value in kwargs.items():
            setattr(driver, field, value)
        await self._s.flush()
        return driver

    async def delete(self, driver_id: int) -> bool:
        driver = await self.get_by_id(driver_id)
        if driver is None:
            return False
        await self._s.delete(driver)
        await self._s.flush()
        return True


class VehicleRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._s = session

    async def get_by_id(self, vehicle_id: int) -> Vehicle | None:
        return await self._s.get(Vehicle, vehicle_id)

    async def list_all(self) -> list[Vehicle]:
        stmt = select(Vehicle)
        return list(await self._s.scalars(stmt))

    async def create(self, **kwargs) -> Vehicle:
        vehicle = Vehicle(**kwargs)
        self._s.add(vehicle)
        await self._s.flush()
        return vehicle

    async def update(self, vehicle_id: int, **kwargs) -> Vehicle | None:
        vehicle = await self.get_by_id(vehicle_id)
        if vehicle is None:
            return None
        for field, value in kwargs.items():
            setattr(vehicle, field, value)
        await self._s.flush()
        return vehicle

    async def delete(self, vehicle_id: int) -> bool:
        vehicle = await self.get_by_id(vehicle_id)
        if vehicle is None:
            return False
        await self._s.delete(vehicle)
        await self._s.flush()
        return True


class RouteRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._s = session

    async def get_by_id(self, route_id: int) -> Route | None:
        return await self._s.get(Route, route_id)

    async def list_all(self) -> list[Route]:
        stmt = select(Route)
        return list(await self._s.scalars(stmt))

    async def create(self, **kwargs) -> Route:
        route = Route(**kwargs)
        self._s.add(route)
        await self._s.flush()
        return route

    async def update(self, route_id: int, **kwargs) -> Route | None:
        route = await self.get_by_id(route_id)
        if route is None:
            return None
        for field, value in kwargs.items():
            setattr(route, field, value)
        await self._s.flush()
        return route

    async def delete(self, route_id: int) -> bool:
        route = await self.get_by_id(route_id)
        if route is None:
            return False
        await self._s.delete(route)
        await self._s.flush()
        return True


class RouteLineRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._s = session

    async def get_by_id(self, line_id: int) -> RouteLine | None:
        return await self._s.get(RouteLine, line_id)

    async def list_all(self) -> list[RouteLine]:
        return list(await self._s.scalars(select(RouteLine)))

    async def list_by_route(self, route_id: int) -> list[RouteLine]:
        stmt = select(RouteLine).where(RouteLine.route_id == route_id)
        return list(await self._s.scalars(stmt))

    async def create(self, **kwargs) -> RouteLine:
        line = RouteLine(**kwargs)
        self._s.add(line)
        await self._s.flush()
        return line

    async def update(self, line_id: int, **kwargs) -> RouteLine | None:
        line = await self.get_by_id(line_id)
        if line is None:
            return None
        for field, value in kwargs.items():
            setattr(line, field, value)
        await self._s.flush()
        return line

    async def delete(self, line_id: int) -> bool:
        line = await self.get_by_id(line_id)
        if line is None:
            return False
        await self._s.delete(line)
        await self._s.flush()
        return True


class DeviationRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._s = session

    async def get_by_id(self, deviation_id: int) -> DeliveryDeviation | None:
        return await self._s.get(DeliveryDeviation, deviation_id)

    async def list_all(self) -> list[DeliveryDeviation]:
        return list(await self._s.scalars(select(DeliveryDeviation)))

    async def list_by_order(self, order_id: int) -> list[DeliveryDeviation]:
        stmt = select(DeliveryDeviation).where(
            DeliveryDeviation.delivery_order_id == order_id
        )
        return list(await self._s.scalars(stmt))

    async def create(self, **kwargs) -> DeliveryDeviation:
        deviation = DeliveryDeviation(**kwargs)
        self._s.add(deviation)
        await self._s.flush()
        return deviation

    async def update(self, deviation_id: int, **kwargs) -> DeliveryDeviation | None:
        deviation = await self.get_by_id(deviation_id)
        if deviation is None:
            return None
        for field, value in kwargs.items():
            setattr(deviation, field, value)
        await self._s.flush()
        return deviation

    async def delete(self, deviation_id: int) -> bool:
        deviation = await self.get_by_id(deviation_id)
        if deviation is None:
            return False
        await self._s.delete(deviation)
        await self._s.flush()
        return True
