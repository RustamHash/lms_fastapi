"""Репозитории для модуля orders."""

from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from app.orders.models import (
    InboundOrder,
    InboundOrderLine,
    OutboundOrder,
    OutboundOrderLine,
    ReturnOrder,
    ReturnOrderLine,
)


class InboundOrderRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._s = session

    async def get_by_id(self, order_id: int) -> InboundOrder | None:
        return await self._s.get(InboundOrder, order_id)

    async def list_all(self) -> list[InboundOrder]:
        stmt = select(InboundOrder)
        return list(await self._s.scalars(stmt))

    async def list_all_detailed(self) -> list[InboundOrder]:
        stmt = (
            select(InboundOrder)
            .options(selectinload(InboundOrder.depositor))
            .options(selectinload(InboundOrder.warehouse))
            .options(selectinload(InboundOrder.supplier))
        )
        return list(await self._s.scalars(stmt))

    async def get_by_number(self, depositor_id: int, number: str) -> InboundOrder | None:
        stmt = select(InboundOrder).where(
            InboundOrder.depositor_id == depositor_id,
            InboundOrder.number == number,
        )
        return await self._s.scalar(stmt)

    async def create(self, **kwargs) -> InboundOrder:
        order = InboundOrder(**kwargs)
        self._s.add(order)
        await self._s.flush()
        return order

    async def update(self, order_id: int, **kwargs) -> InboundOrder | None:
        order = await self.get_by_id(order_id)
        if order is None:
            return None
        for field, value in kwargs.items():
            setattr(order, field, value)
        await self._s.flush()
        return order


class InboundOrderLineRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._s = session

    async def get_by_id(self, line_id: int) -> InboundOrderLine | None:
        return await self._s.get(InboundOrderLine, line_id)

    async def list_by_order(self, order_id: int) -> list[InboundOrderLine]:
        stmt = select(InboundOrderLine).where(InboundOrderLine.order_id == order_id)
        return list(await self._s.scalars(stmt))

    async def create(self, **kwargs) -> InboundOrderLine:
        line = InboundOrderLine(**kwargs)
        self._s.add(line)
        await self._s.flush()
        return line

    async def update(self, line_id: int, **kwargs) -> InboundOrderLine | None:
        line = await self.get_by_id(line_id)
        if line is None:
            return None
        for field, value in kwargs.items():
            setattr(line, field, value)
        await self._s.flush()
        return line


class OutboundOrderRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._s = session

    async def get_by_id(self, order_id: int) -> OutboundOrder | None:
        return await self._s.get(OutboundOrder, order_id)

    async def list_all(self) -> list[OutboundOrder]:
        stmt = select(OutboundOrder)
        return list(await self._s.scalars(stmt))

    async def list_all_detailed(self) -> list[OutboundOrder]:
        stmt = (
            select(OutboundOrder)
            .options(selectinload(OutboundOrder.depositor))
            .options(selectinload(OutboundOrder.client))
            .options(selectinload(OutboundOrder.warehouse))
        )
        return list(await self._s.scalars(stmt))

    async def get_by_number(self, depositor_id: int, number: str) -> OutboundOrder | None:
        stmt = select(OutboundOrder).where(
            OutboundOrder.depositor_id == depositor_id,
            OutboundOrder.number == number,
        )
        return await self._s.scalar(stmt)

    async def create(self, **kwargs) -> OutboundOrder:
        order = OutboundOrder(**kwargs)
        self._s.add(order)
        await self._s.flush()
        return order

    async def update(self, order_id: int, **kwargs) -> OutboundOrder | None:
        order = await self.get_by_id(order_id)
        if order is None:
            return None
        for field, value in kwargs.items():
            setattr(order, field, value)
        await self._s.flush()
        return order


class OutboundOrderLineRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._s = session

    async def get_by_id(self, line_id: int) -> OutboundOrderLine | None:
        return await self._s.get(OutboundOrderLine, line_id)

    async def list_by_order(self, order_id: int) -> list[OutboundOrderLine]:
        stmt = select(OutboundOrderLine).where(OutboundOrderLine.order_id == order_id)
        return list(await self._s.scalars(stmt))

    async def create(self, **kwargs) -> OutboundOrderLine:
        line = OutboundOrderLine(**kwargs)
        self._s.add(line)
        await self._s.flush()
        return line

    async def update(self, line_id: int, **kwargs) -> OutboundOrderLine | None:
        line = await self.get_by_id(line_id)
        if line is None:
            return None
        for field, value in kwargs.items():
            setattr(line, field, value)
        await self._s.flush()
        return line


class ReturnOrderRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._s = session

    async def get_by_id(self, order_id: int) -> ReturnOrder | None:
        return await self._s.get(ReturnOrder, order_id)

    async def list_all(self) -> list[ReturnOrder]:
        stmt = select(ReturnOrder)
        return list(await self._s.scalars(stmt))

    async def create(self, **kwargs) -> ReturnOrder:
        order = ReturnOrder(**kwargs)
        self._s.add(order)
        await self._s.flush()
        return order

    async def update(self, order_id: int, **kwargs) -> ReturnOrder | None:
        order = await self.get_by_id(order_id)
        if order is None:
            return None
        for field, value in kwargs.items():
            setattr(order, field, value)
        await self._s.flush()
        return order


class ReturnOrderLineRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._s = session

    async def get_by_id(self, line_id: int) -> ReturnOrderLine | None:
        return await self._s.get(ReturnOrderLine, line_id)

    async def list_by_order(self, order_id: int) -> list[ReturnOrderLine]:
        stmt = select(ReturnOrderLine).where(ReturnOrderLine.return_order_id == order_id)
        return list(await self._s.scalars(stmt))

    async def create(self, **kwargs) -> ReturnOrderLine:
        line = ReturnOrderLine(**kwargs)
        self._s.add(line)
        await self._s.flush()
        return line

    async def update(self, line_id: int, **kwargs) -> ReturnOrderLine | None:
        line = await self.get_by_id(line_id)
        if line is None:
            return None
        for field, value in kwargs.items():
            setattr(line, field, value)
        await self._s.flush()
        return line
