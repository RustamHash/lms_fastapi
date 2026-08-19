"""Сервис заказов на доставку."""

from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.delivery.models import DeliveryOrder


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
        stmt = select(DeliveryOrder).where(DeliveryOrder.is_deleted.is_(False))
        return list(await self._s.scalars(stmt))

    async def list_by_trade_point(self, trade_point_id: int) -> list[DeliveryOrder]:
        stmt = select(DeliveryOrder).where(
            DeliveryOrder.trade_point_id == trade_point_id,
            DeliveryOrder.is_deleted.is_(False),
        )
        return list(await self._s.scalars(stmt))
