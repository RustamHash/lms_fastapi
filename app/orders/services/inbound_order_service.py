"""Сервис входящих заказов."""

from __future__ import annotations

from app.accounts.scope import DataScope
from app.core.exceptions import ForbiddenError
from app.orders.models import InboundOrder, InboundOrderLine
from app.orders.repository import InboundOrderLineRepository, InboundOrderRepository


class InboundOrderService:
    def __init__(
        self,
        order_repo: InboundOrderRepository,
        line_repo: InboundOrderLineRepository,
    ) -> None:
        self._orders = order_repo
        self._lines = line_repo

    async def get_by_id(
        self, order_id: int, scope: DataScope | None = None
    ) -> InboundOrder | None:
        return await self._orders.get_by_id(order_id, scope=scope)

    async def list_all(self, scope: DataScope | None = None) -> list[InboundOrder]:
        return await self._orders.list_all(scope=scope)

    async def create(self, *, scope: DataScope, depositor_id: int, **kwargs) -> InboundOrder:
        if not scope.allows_depositor(depositor_id):
            raise ForbiddenError("Нет доступа к этому поклажедателю")
        return await self._orders.create(depositor_id=depositor_id, **kwargs)

    async def update(
        self, order_id: int, scope: DataScope, **kwargs
    ) -> InboundOrder | None:
        order = await self._orders.get_by_id(order_id, scope=scope)
        if order is None:
            return None
        if "depositor_id" in kwargs and not scope.allows_depositor(kwargs["depositor_id"]):
            raise ForbiddenError("Нет доступа к этому поклажедателю")
        return await self._orders.update(order_id, **kwargs)

    async def soft_delete(
        self, order_id: int, user_id: int | None = None, scope: DataScope | None = None
    ) -> bool:
        order = await self._orders.get_by_id(order_id, scope=scope)
        if order is None:
            return False
        return await self._orders.soft_delete(order_id, user_id)

    async def list_lines(self, order_id: int) -> list[InboundOrderLine]:
        return await self._lines.list_by_order(order_id)

    async def add_line(self, *, user_id: int | None = None, order_id: int, **kwargs) -> InboundOrderLine:
        return await self._lines.create(order_id=order_id, **kwargs)

    async def update_line(self, line_id: int, user_id: int | None = None, **kwargs) -> InboundOrderLine | None:
        return await self._lines.update(line_id, **kwargs)

    async def delete_line(self, line_id: int, user_id: int | None = None) -> bool:
        return await self._lines.soft_delete(line_id, user_id)
