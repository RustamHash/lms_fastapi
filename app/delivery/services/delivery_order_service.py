"""Сервис заказов на доставку."""

from __future__ import annotations

from app.delivery.repository import DeliveryOrderRepository
from app.infrastructure.events import event_bus
from app.infrastructure.events.event_types import EventTypes


class DeliveryOrderService:
    def __init__(self, repo: DeliveryOrderRepository) -> None:
        self._repo = repo

    async def create(self, *, user_id: int, **kwargs) -> object:
        order = await self._repo.create(
            **kwargs,
        )

        # Отправить событие
        await event_bus.emit(EventTypes.DELIVERY_ORDER_CREATED, {
            "_event_type": EventTypes.DELIVERY_ORDER_CREATED,
            "order_id": order.id,
            "order_number": order.number,
        })

        return order

    async def get_by_id(self, order_id: int):
        return await self._repo.get_by_id(order_id)

    async def set_status(self, *, user_id: int, order_id: int, status: str):
        return await self._repo.update(order_id, status=status)

    async def assign(self, *, user_id: int, order_id: int):
        return await self.set_status(user_id=user_id, order_id=order_id, status="assigned")

    async def mark_in_transit(self, *, user_id: int, order_id: int):
        return await self.set_status(user_id=user_id, order_id=order_id, status="in_transit")

    async def mark_delivered(self, *, user_id: int, order_id: int):
        return await self.set_status(user_id=user_id, order_id=order_id, status="delivered")

    async def cancel(self, *, user_id: int, order_id: int):
        return await self.set_status(user_id=user_id, order_id=order_id, status="cancelled")

    async def list_all(self):
        return await self._repo.list_all()
