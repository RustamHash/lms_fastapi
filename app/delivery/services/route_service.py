"""Сервис маршрутов."""

from __future__ import annotations

from app.core.exceptions import NotFoundError
from app.core.statuses import DeliveryStatus
from app.delivery.models import Route, RouteLine
from app.delivery.repository import (
    DeliveryOrderRepository,
    RouteLineRepository,
    RouteRepository,
)
from app.infrastructure.events import schedule_event
from app.infrastructure.events.event_types import EventTypes


class RouteService:
    def __init__(
        self,
        repo: RouteRepository,
        lines: RouteLineRepository | None = None,
        delivery_orders: DeliveryOrderRepository | None = None,
    ) -> None:
        self._repo = repo
        self._lines = lines or RouteLineRepository(repo._s)
        self._delivery_orders = delivery_orders or DeliveryOrderRepository(repo._s)

    async def get_by_id(self, route_id: int) -> Route | None:
        return await self._repo.get_by_id(route_id)

    async def list_all(self) -> list[Route]:
        return await self._repo.list_all()

    async def create(self, *, user_id: int | None = None, **kwargs) -> Route:
        return await self._repo.create(**kwargs)

    async def update(self, route_id: int, user_id: int | None = None, **kwargs) -> Route | None:
        return await self._repo.update(route_id, **kwargs)

    async def soft_delete(self, route_id: int, user_id: int | None = None) -> bool:
        return await self._repo.soft_delete(route_id, user_id)

    async def assign_order(
        self,
        route_id: int,
        delivery_order_id: int,
        user_id: int | None = None,
    ) -> RouteLine:
        """Привязать заказ доставки к маршруту (создать RouteLine при необходимости)."""
        route = await self._repo.get_by_id(route_id)
        if route is None:
            raise NotFoundError("Маршрут не найден")

        delivery = await self._delivery_orders.get_by_id(delivery_order_id)
        if delivery is None:
            raise NotFoundError("Заказ на доставку не найден")

        existing_lines = await self._lines.list_by_route(route_id)
        for line in existing_lines:
            if line.delivery_order_id == delivery_order_id and not line.is_deleted:
                return line

        next_order = max((ln.order for ln in existing_lines), default=0) + 1
        line = await self._lines.create(
            route_id=route_id,
            delivery_order_id=delivery_order_id,
            order=next_order,
            status="pending",
            created_by_id=user_id,
            updated_by_id=user_id,
        )

        if delivery.status == DeliveryStatus.CREATED.value:
            await self._delivery_orders.update(
                delivery_order_id,
                status=DeliveryStatus.ASSIGNED.value,
            )

        schedule_event(
            self._repo._s,
            EventTypes.ROUTE_ASSIGNED,
            {
                "route_id": route_id,
                "delivery_order_id": delivery_order_id,
                "route_line_id": line.id,
            },
        )
        return line
