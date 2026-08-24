"""Сервис возвратов."""

from __future__ import annotations

from app.orders.models import ReturnOrder, ReturnOrderLine
from app.orders.repository import ReturnOrderLineRepository, ReturnOrderRepository


class ReturnOrderService:
    def __init__(
        self,
        order_repo: ReturnOrderRepository,
        line_repo: ReturnOrderLineRepository,
    ) -> None:
        self._orders = order_repo
        self._lines = line_repo

    async def get_by_id(self, order_id: int) -> ReturnOrder | None:
        return await self._orders.get_by_id(order_id)

    async def list_all(self) -> list[ReturnOrder]:
        return await self._orders.list_all()

    async def create(self, *, user_id: int | None = None, **kwargs) -> ReturnOrder:
        return await self._orders.create(**kwargs)

    async def update(self, order_id: int, user_id: int | None = None, **kwargs) -> ReturnOrder | None:
        return await self._orders.update(order_id, **kwargs)

    async def soft_delete(self, order_id: int, user_id: int | None = None) -> bool:
        return await self._orders.soft_delete(order_id, user_id)

    async def list_lines(self, order_id: int) -> list[ReturnOrderLine]:
        return await self._lines.list_by_order(order_id)

    async def add_line(self, *, user_id: int | None = None, return_order_id: int, **kwargs) -> ReturnOrderLine:
        return await self._lines.create(return_order_id=return_order_id, **kwargs)

    async def delete_line(self, line_id: int, user_id: int | None = None) -> bool:
        return await self._lines.soft_delete(line_id, user_id)
