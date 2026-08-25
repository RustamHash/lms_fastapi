"""Сервис заказов на доставку."""

from __future__ import annotations

from app.delivery.models import DeliveryOrder
from app.delivery.repository import DeliveryOrderRepository
from app.infrastructure.events import schedule_event
from app.infrastructure.events.event_types import EventTypes


class DeliveryOrderService:
    def __init__(self, repo: DeliveryOrderRepository) -> None:
        self._repo = repo

    async def get_by_id(self, order_id: int) -> DeliveryOrder | None:
        return await self._repo.get_by_id(order_id)

    async def list_all(self) -> list[DeliveryOrder]:
        return await self._repo.list_all()

    async def create(self, *, user_id: int | None = None, **kwargs) -> DeliveryOrder:
        order = await self._repo.create(**kwargs)

        schedule_event(self._repo._s, EventTypes.DELIVERY_ORDER_CREATED, {
            "order_id": order.id,
            "order_number": order.number,
        })

        return order

    async def update(self, order_id: int, user_id: int | None = None, **kwargs) -> DeliveryOrder | None:
        return await self._repo.update(order_id, **kwargs)

    async def soft_delete(self, order_id: int, user_id: int | None = None) -> bool:
        return await self._repo.soft_delete(order_id, user_id)

    async def set_status(self, *, user_id: int, order_id: int, status: str) -> DeliveryOrder | None:
        return await self._repo.update(order_id, status=status)
