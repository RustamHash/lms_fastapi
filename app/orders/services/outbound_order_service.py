"""Сервис исходящих заказов."""

from __future__ import annotations

from app.orders.models import OutboundOrder, OutboundOrderLine
from app.orders.repository import OutboundOrderLineRepository, OutboundOrderRepository


class OutboundOrderService:
    def __init__(
        self,
        order_repo: OutboundOrderRepository,
        line_repo: OutboundOrderLineRepository,
    ) -> None:
        self._orders = order_repo
        self._lines = line_repo

    async def get_by_id(self, order_id: int) -> OutboundOrder | None:
        return await self._orders.get_by_id(order_id)

    async def list_all(self) -> list[OutboundOrder]:
        return await self._orders.list_all()

    async def create(self, *, user_id: int | None = None, **kwargs) -> OutboundOrder:
        return await self._orders.create(**kwargs)

    async def update(self, order_id: int, user_id: int | None = None, **kwargs) -> OutboundOrder | None:
        return await self._orders.update(order_id, **kwargs)

    async def soft_delete(self, order_id: int, user_id: int | None = None) -> bool:
        return await self._orders.soft_delete(order_id, user_id)

    async def list_lines(self, order_id: int) -> list[OutboundOrderLine]:
        return await self._lines.list_by_order(order_id)

    async def add_line(self, *, user_id: int | None = None, order_id: int, **kwargs) -> OutboundOrderLine:
        return await self._lines.create(order_id=order_id, **kwargs)

    async def update_line(self, line_id: int, user_id: int | None = None, **kwargs) -> OutboundOrderLine | None:
        return await self._lines.update(line_id, **kwargs)

    async def delete_line(self, line_id: int, user_id: int | None = None) -> bool:
        return await self._lines.soft_delete(line_id, user_id)
