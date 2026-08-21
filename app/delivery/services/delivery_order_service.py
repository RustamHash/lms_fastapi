"""Сервис заказов на доставку."""

from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.delivery.models import DeliveryOrder
from app.infrastructure.events import event_bus
from app.infrastructure.events.event_types import EventTypes


class DeliveryOrderService:
    def __init__(self, session: AsyncSession) -> None:
        self._s = session

    async def create(self, *, user_id: int, **kwargs) -> DeliveryOrder:
        order = DeliveryOrder(
            created_by_id=user_id,
            updated_by_id=user_id,
            **kwargs,
        )
        self._s.add(order)
        await self._s.flush()

        # Отправить событие
        await event_bus.emit(EventTypes.DELIVERY_ORDER_CREATED, {
            "_event_type": EventTypes.DELIVERY_ORDER_CREATED,
            "order_id": order.id,
            "order_number": order.number,
        })

        return order

    async def get_by_id(self, order_id: int) -> DeliveryOrder | None:
        return await self._s.get(DeliveryOrder, order_id)

    async def set_status(self, *, user_id: int, order_id: int, status: str) -> DeliveryOrder | None:
        order = await self._s.get(DeliveryOrder, order_id)
        if order is None:
            return None
        order.status = status
        order.updated_by_id = user_id
        await self._s.flush()
        return order

    async def assign(self, *, user_id: int, order_id: int) -> DeliveryOrder | None:
        return await self.set_status(user_id=user_id, order_id=order_id, status="assigned")

    async def mark_in_transit(self, *, user_id: int, order_id: int) -> DeliveryOrder | None:
        return await self.set_status(user_id=user_id, order_id=order_id, status="in_transit")

    async def mark_delivered(self, *, user_id: int, order_id: int) -> DeliveryOrder | None:
        return await self.set_status(user_id=user_id, order_id=order_id, status="delivered")

    async def cancel(self, *, user_id: int, order_id: int) -> DeliveryOrder | None:
        return await self.set_status(user_id=user_id, order_id=order_id, status="cancelled")

    async def list_all(self) -> list[DeliveryOrder]:
        stmt = select(DeliveryOrder).where()
        return list(await self._s.scalars(stmt))
