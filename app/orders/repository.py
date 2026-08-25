# app/orders/repository.py

"""Репозитории для модуля orders."""

from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.orders.models import InboundOrder, InboundOrderLine, OutboundOrder, OutboundOrderLine, ReturnOrder, ReturnOrderLine


class InboundOrderRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._s = session

    async def get_by_id(self, id: int) -> InboundOrder | None:
        stmt = select(InboundOrder).where(InboundOrder.id == id).options(selectinload(InboundOrder.depositor), selectinload(InboundOrder.supplier), selectinload(InboundOrder.warehouse), selectinload(InboundOrder.lines))
        return await self._s.scalar(stmt)

    async def list_all(self) -> list[InboundOrder]:
        stmt = select(InboundOrder).options(selectinload(InboundOrder.depositor), selectinload(InboundOrder.supplier), selectinload(InboundOrder.warehouse))
        return list(await self._s.scalars(stmt))

    async def get_by_depositor_number(
        self, depositor_id: int, number: str
    ) -> InboundOrder | None:
        stmt = select(InboundOrder).where(
            InboundOrder.depositor_id == depositor_id,
            InboundOrder.number == number,
        )
        return await self._s.scalar(stmt)

    async def create(self, **kwargs) -> InboundOrder:
        row = InboundOrder(**kwargs)
        self._s.add(row)
        await self._s.flush()
        return row

    async def update(self, id: int, **kwargs) -> InboundOrder | None:
        row = await self._s.get(InboundOrder, id)
        if row is None:
            return None
        for field, value in kwargs.items():
            setattr(row, field, value)
        await self._s.flush()
        return row

    async def soft_delete(self, id: int, user_id: int | None = None) -> bool:
        row = await self._s.get(InboundOrder, id)
        if row is None:
            return False
        row.soft_delete(user_id)
        await self._s.flush()
        return True


class InboundOrderLineRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._s = session

    async def get_by_id(self, id: int) -> InboundOrderLine | None:
        return await self._s.get(InboundOrderLine, id)

    async def list_all(self) -> list[InboundOrderLine]:
        return list(await self._s.scalars(select(InboundOrderLine)))

    async def list_by_order(self, order_id: int) -> list[InboundOrderLine]:
        stmt = select(InboundOrderLine).where(InboundOrderLine.order_id == order_id)
        return list(await self._s.scalars(stmt))

    async def create(self, **kwargs) -> InboundOrderLine:
        row = InboundOrderLine(**kwargs)
        self._s.add(row)
        await self._s.flush()
        return row

    async def update(self, id: int, **kwargs) -> InboundOrderLine | None:
        row = await self._s.get(InboundOrderLine, id)
        if row is None:
            return None
        for field, value in kwargs.items():
            setattr(row, field, value)
        await self._s.flush()
        return row

    async def soft_delete(self, id: int, user_id: int | None = None) -> bool:
        row = await self._s.get(InboundOrderLine, id)
        if row is None:
            return False
        row.soft_delete(user_id)
        await self._s.flush()
        return True


class OutboundOrderRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._s = session

    async def get_by_id(self, id: int) -> OutboundOrder | None:
        stmt = select(OutboundOrder).where(OutboundOrder.id == id).options(selectinload(OutboundOrder.depositor), selectinload(OutboundOrder.client), selectinload(OutboundOrder.warehouse), selectinload(OutboundOrder.lines))
        return await self._s.scalar(stmt)

    async def list_all(self) -> list[OutboundOrder]:
        stmt = select(OutboundOrder).options(selectinload(OutboundOrder.depositor), selectinload(OutboundOrder.client), selectinload(OutboundOrder.warehouse))
        return list(await self._s.scalars(stmt))

    async def create(self, **kwargs) -> OutboundOrder:
        row = OutboundOrder(**kwargs)
        self._s.add(row)
        await self._s.flush()
        return row

    async def update(self, id: int, **kwargs) -> OutboundOrder | None:
        row = await self._s.get(OutboundOrder, id)
        if row is None:
            return None
        for field, value in kwargs.items():
            setattr(row, field, value)
        await self._s.flush()
        return row

    async def soft_delete(self, id: int, user_id: int | None = None) -> bool:
        row = await self._s.get(OutboundOrder, id)
        if row is None:
            return False
        row.soft_delete(user_id)
        await self._s.flush()
        return True


class OutboundOrderLineRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._s = session

    async def get_by_id(self, id: int) -> OutboundOrderLine | None:
        return await self._s.get(OutboundOrderLine, id)

    async def list_all(self) -> list[OutboundOrderLine]:
        return list(await self._s.scalars(select(OutboundOrderLine)))

    async def list_by_order(self, order_id: int) -> list[OutboundOrderLine]:
        stmt = select(OutboundOrderLine).where(OutboundOrderLine.order_id == order_id)
        return list(await self._s.scalars(stmt))

    async def create(self, **kwargs) -> OutboundOrderLine:
        row = OutboundOrderLine(**kwargs)
        self._s.add(row)
        await self._s.flush()
        return row

    async def update(self, id: int, **kwargs) -> OutboundOrderLine | None:
        row = await self._s.get(OutboundOrderLine, id)
        if row is None:
            return None
        for field, value in kwargs.items():
            setattr(row, field, value)
        await self._s.flush()
        return row

    async def soft_delete(self, id: int, user_id: int | None = None) -> bool:
        row = await self._s.get(OutboundOrderLine, id)
        if row is None:
            return False
        row.soft_delete(user_id)
        await self._s.flush()
        return True


class ReturnOrderRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._s = session

    async def get_by_id(self, id: int) -> ReturnOrder | None:
        return await self._s.get(ReturnOrder, id)

    async def list_all(self) -> list[ReturnOrder]:
        return list(await self._s.scalars(select(ReturnOrder)))

    async def create(self, **kwargs) -> ReturnOrder:
        row = ReturnOrder(**kwargs)
        self._s.add(row)
        await self._s.flush()
        return row

    async def update(self, id: int, **kwargs) -> ReturnOrder | None:
        row = await self._s.get(ReturnOrder, id)
        if row is None:
            return None
        for field, value in kwargs.items():
            setattr(row, field, value)
        await self._s.flush()
        return row

    async def soft_delete(self, id: int, user_id: int | None = None) -> bool:
        row = await self._s.get(ReturnOrder, id)
        if row is None:
            return False
        row.soft_delete(user_id)
        await self._s.flush()
        return True


class ReturnOrderLineRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._s = session

    async def get_by_id(self, id: int) -> ReturnOrderLine | None:
        return await self._s.get(ReturnOrderLine, id)

    async def list_all(self) -> list[ReturnOrderLine]:
        return list(await self._s.scalars(select(ReturnOrderLine)))

    async def list_by_order(self, order_id: int) -> list[ReturnOrderLine]:
        stmt = select(ReturnOrderLine).where(ReturnOrderLine.return_order_id == order_id)
        return list(await self._s.scalars(stmt))

    async def create(self, **kwargs) -> ReturnOrderLine:
        row = ReturnOrderLine(**kwargs)
        self._s.add(row)
        await self._s.flush()
        return row

    async def update(self, id: int, **kwargs) -> ReturnOrderLine | None:
        row = await self._s.get(ReturnOrderLine, id)
        if row is None:
            return None
        for field, value in kwargs.items():
            setattr(row, field, value)
        await self._s.flush()
        return row

    async def soft_delete(self, id: int, user_id: int | None = None) -> bool:
        row = await self._s.get(ReturnOrderLine, id)
        if row is None:
            return False
        row.soft_delete(user_id)
        await self._s.flush()
        return True
