"""Сервис возвратов."""

from __future__ import annotations

from app.accounts.scope import DataScope
from app.core.exceptions import ForbiddenError, NotFoundError
from app.orders.models import OutboundOrder, ReturnOrder, ReturnOrderLine
from app.orders.repository import ReturnOrderLineRepository, ReturnOrderRepository


class ReturnOrderService:
    def __init__(
        self,
        order_repo: ReturnOrderRepository,
        line_repo: ReturnOrderLineRepository,
    ) -> None:
        self._orders = order_repo
        self._lines = line_repo

    async def get_by_id(
        self, order_id: int, scope: DataScope | None = None
    ) -> ReturnOrder | None:
        return await self._orders.get_by_id(order_id, scope=scope)

    async def list_all(self, scope: DataScope | None = None) -> list[ReturnOrder]:
        return await self._orders.list_all(scope=scope)

    async def create(self, *, scope: DataScope, outbound_order_id: int, **kwargs) -> ReturnOrder:
        outbound = await self._orders._s.get(OutboundOrder, outbound_order_id)
        if outbound is None or outbound.is_deleted:
            raise NotFoundError("Исходящий заказ не найден")
        if not scope.allows_client(outbound.client_id, outbound.depositor_id):
            raise ForbiddenError("Нет доступа к этому заказу")
        kwargs.pop("customer_code", None)
        kwargs.pop("customer_name", None)
        kwargs.pop("client_id", None)
        kwargs["depositor_id"] = outbound.depositor_id
        return await self._orders.create(
            outbound_order_id=outbound_order_id,
            client_id=outbound.client_id,
            customer_code=outbound.customer_code,
            customer_name=outbound.customer_name,
            **kwargs,
        )

    async def update(
        self, order_id: int, scope: DataScope, **kwargs
    ) -> ReturnOrder | None:
        order = await self._orders.get_by_id(order_id, scope=scope)
        if order is None:
            return None
        return await self._orders.update(order_id, **kwargs)

    async def soft_delete(
        self, order_id: int, user_id: int | None = None, scope: DataScope | None = None
    ) -> bool:
        order = await self._orders.get_by_id(order_id, scope=scope)
        if order is None:
            return False
        return await self._orders.soft_delete(order_id, user_id)

    async def list_lines(self, order_id: int) -> list[ReturnOrderLine]:
        return await self._lines.list_by_order(order_id)

    async def add_line(self, *, user_id: int | None = None, return_order_id: int, **kwargs) -> ReturnOrderLine:
        return await self._lines.create(return_order_id=return_order_id, **kwargs)

    async def delete_line(self, line_id: int, user_id: int | None = None) -> bool:
        return await self._lines.soft_delete(line_id, user_id)
