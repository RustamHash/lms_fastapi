"""Сервис остатков и движений."""

from __future__ import annotations

from decimal import Decimal

import logging

from sqlalchemy import select

logger = logging.getLogger(__name__)
from sqlalchemy.ext.asyncio import AsyncSession

from app.warehouse.models import StockBalance, StockMovement


class StockService:
    def __init__(self, session: AsyncSession) -> None:
        self._s = session

    async def get_balance(
        self,
        product_id: int,
        location_id: int,
        lpn_id: int | None = None,
        batch_id: int | None = None,
    ) -> StockBalance | None:
        stmt = select(StockBalance).where(
            StockBalance.product_id == product_id,
            StockBalance.location_id == location_id,
            StockBalance.lpn_id == lpn_id,
            StockBalance.batch_id == batch_id,
        )
        return await self._s.scalar(stmt)

    async def get_available_quantity(
        self,
        product_id: int,
        location_id: int | None = None,
        lpn_id: int | None = None,
        batch_id: int | None = None,
    ) -> Decimal:
        stmt = select(StockBalance).where(
            StockBalance.product_id == product_id,
        )
        if location_id:
            stmt = stmt.where(StockBalance.location_id == location_id)
        if lpn_id:
            stmt = stmt.where(StockBalance.lpn_id == lpn_id)
        if batch_id:
            stmt = stmt.where(StockBalance.batch_id == batch_id)

        balances = await self._s.scalars(stmt)
        total = Decimal("0")
        for b in balances:
            total += b.quantity - b.reserved_quantity
        return total

    async def add_stock(
        self,
        *,
        user_id: int,
        product_id: int,
        location_id: int,
        quantity: Decimal,
        lpn_id: int | None = None,
        batch_id: int | None = None,
        document_id: int | None = None,
    ) -> StockBalance:
        if quantity <= 0:
            raise ValueError("Количество должно быть больше 0")

        balance = await self.get_balance(product_id, location_id, lpn_id, batch_id)

        if balance:
            balance.quantity += quantity
            balance.updated_by_id = user_id
        else:
            balance = StockBalance(
                product_id=product_id,
                location_id=location_id,
                lpn_id=lpn_id,
                batch_id=batch_id,
                quantity=quantity,
                reserved_quantity=Decimal("0"),
                created_by_id=user_id,
                updated_by_id=user_id,
            )
            self._s.add(balance)

        await self._s.flush()

        logger.info("Приход: product=%s, qty=%s, location=%s", product_id, quantity, location_id)
        movement = StockMovement(
            product_id=product_id,
            document_id=document_id,
            location_id=location_id,
            lpn_id=lpn_id,
            batch_id=batch_id,
            direction="in",
            quantity=quantity,
            created_by_id=user_id,
            updated_by_id=user_id,
        )
        self._s.add(movement)
        await self._s.flush()

        return balance

    async def remove_stock(
        self,
        *,
        user_id: int,
        product_id: int,
        location_id: int,
        quantity: Decimal,
        lpn_id: int | None = None,
        batch_id: int | None = None,
        document_id: int | None = None,
    ) -> StockBalance:
        if quantity <= 0:
            raise ValueError("Количество должно быть больше 0")

        balance = await self.get_balance(product_id, location_id, lpn_id, batch_id)

        if not balance:
            raise ValueError("Нет остатка для списания")

        if balance.quantity < quantity:
            raise ValueError(f"Недостаточно остатка: {balance.quantity} < {quantity}")

        balance.quantity -= quantity
        balance.updated_by_id = user_id
        await self._s.flush()

        logger.info("Приход: product=%s, qty=%s, location=%s", product_id, quantity, location_id)
        logger.info("Расход: product=%s, qty=%s, location=%s", product_id, quantity, location_id)
        movement = StockMovement(
            product_id=product_id,
            document_id=document_id,
            location_id=location_id,
            lpn_id=lpn_id,
            batch_id=batch_id,
            direction="out",
            quantity=quantity,
            created_by_id=user_id,
            updated_by_id=user_id,
        )
        self._s.add(movement)
        await self._s.flush()

        return balance

    async def move_stock(
        self,
        *,
        user_id: int,
        product_id: int,
        from_location_id: int,
        to_location_id: int,
        quantity: Decimal,
        lpn_id: int | None = None,
        batch_id: int | None = None,
        document_id: int | None = None,
    ) -> StockBalance:
        await self.remove_stock(
            user_id=user_id,
            product_id=product_id,
            location_id=from_location_id,
            quantity=quantity,
            lpn_id=lpn_id,
            batch_id=batch_id,
            document_id=document_id,
        )

        return await self.add_stock(
            user_id=user_id,
            product_id=product_id,
            location_id=to_location_id,
            quantity=quantity,
            lpn_id=lpn_id,
            batch_id=batch_id,
            document_id=document_id,
        )

    async def reserve(
        self,
        *,
        user_id: int,
        product_id: int,
        location_id: int,
        quantity: Decimal,
        lpn_id: int | None = None,
        batch_id: int | None = None,
    ) -> StockBalance:
        balance = await self.get_balance(product_id, location_id, lpn_id, batch_id)

        if not balance:
            raise ValueError("Нет остатка для резервирования")

        available = balance.quantity - balance.reserved_quantity
        if available < quantity:
            raise ValueError(f"Недостаточно доступного остатка: {available} < {quantity}")

        balance.reserved_quantity += quantity
        balance.updated_by_id = user_id
        await self._s.flush()
        return balance

    async def unreserve(
        self,
        *,
        user_id: int,
        product_id: int,
        location_id: int,
        quantity: Decimal,
        lpn_id: int | None = None,
        batch_id: int | None = None,
    ) -> StockBalance:
        balance = await self.get_balance(product_id, location_id, lpn_id, batch_id)

        if not balance:
            raise ValueError("Нет остатка для отмены резервирования")

        if balance.reserved_quantity < quantity:
            raise ValueError("Недостаточно зарезервированного")

        balance.reserved_quantity -= quantity
        balance.updated_by_id = user_id
        await self._s.flush()
        return balance
