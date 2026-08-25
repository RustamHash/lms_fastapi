"""Сервис исходящих заказов."""

from __future__ import annotations

from app.accounts.scope import DataScope
from app.core.exceptions import BadRequestError, ForbiddenError, NotFoundError
from app.orders.models import OutboundOrder, OutboundOrderLine
from app.orders.repository import OutboundOrderLineRepository, OutboundOrderRepository
from app.parties.models import Client


class OutboundOrderService:
    def __init__(
        self,
        order_repo: OutboundOrderRepository,
        line_repo: OutboundOrderLineRepository,
    ) -> None:
        self._orders = order_repo
        self._lines = line_repo

    async def get_by_id(
        self, order_id: int, scope: DataScope | None = None
    ) -> OutboundOrder | None:
        return await self._orders.get_by_id(order_id, scope=scope)

    async def list_all(self, scope: DataScope | None = None) -> list[OutboundOrder]:
        return await self._orders.list_all(scope=scope)

    async def create(
        self,
        *,
        scope: DataScope,
        depositor_id: int,
        client_id: int,
        **kwargs,
    ) -> OutboundOrder:
        client = await self._resolve_client(client_id, depositor_id, scope)
        kwargs.pop("customer_code", None)
        kwargs.pop("customer_name", None)
        return await self._orders.create(
            depositor_id=depositor_id,
            client_id=client.id,
            customer_code=client.code,
            customer_name=client.name,
            **kwargs,
        )

    async def update(
        self,
        order_id: int,
        scope: DataScope,
        **kwargs,
    ) -> OutboundOrder | None:
        order = await self._orders.get_by_id(order_id, scope=scope)
        if order is None:
            return None
        client_id = kwargs.pop("client_id", None)
        if client_id is not None:
            depositor_id = kwargs.get("depositor_id", order.depositor_id)
            client = await self._resolve_client(client_id, depositor_id, scope)
            kwargs["client_id"] = client.id
            kwargs["customer_code"] = client.code
            kwargs["customer_name"] = client.name
        return await self._orders.update(order_id, **kwargs)

    async def soft_delete(
        self, order_id: int, user_id: int | None = None, scope: DataScope | None = None
    ) -> bool:
        order = await self._orders.get_by_id(order_id, scope=scope)
        if order is None:
            return False
        return await self._orders.soft_delete(order_id, user_id)

    async def list_lines(self, order_id: int) -> list[OutboundOrderLine]:
        return await self._lines.list_by_order(order_id)

    async def add_line(self, *, user_id: int | None = None, order_id: int, **kwargs) -> OutboundOrderLine:
        return await self._lines.create(order_id=order_id, **kwargs)

    async def update_line(self, line_id: int, user_id: int | None = None, **kwargs) -> OutboundOrderLine | None:
        return await self._lines.update(line_id, **kwargs)

    async def delete_line(self, line_id: int, user_id: int | None = None) -> bool:
        return await self._lines.soft_delete(line_id, user_id)

    async def _resolve_client(
        self, client_id: int, depositor_id: int, scope: DataScope
    ) -> Client:
        client = await self._orders._s.get(Client, client_id)
        if client is None or client.is_deleted:
            raise NotFoundError("Клиент не найден")
        if client.depositor_id != depositor_id:
            raise BadRequestError("Клиент не принадлежит поклажедателю")
        if not scope.allows_client(client.id, client.depositor_id):
            raise ForbiddenError("Нет доступа к этому клиенту")
        return client
