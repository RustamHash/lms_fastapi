"""Сервис остатков."""

from __future__ import annotations

from decimal import Decimal

import logging

from app.warehouse.models import StockBalance
from app.warehouse.repository import StockRepository

logger = logging.getLogger(__name__)


class StockService:
    def __init__(self, repo: StockRepository) -> None:
        self._repo = repo

    async def get_by_id(self, balance_id: int) -> StockBalance | None:
        return await self._repo.get_by_id(balance_id)

    async def list_all(self) -> list[StockBalance]:
        return await self._repo.list_all()

    async def get_balance(
        self, product_id: int, location_id: int, lpn_id: int | None = None, batch_id: int | None = None
    ) -> StockBalance | None:
        return await self._repo.get_balance(product_id, location_id, lpn_id, batch_id)

    async def get_available_quantity(
        self, product_id: int, location_id: int | None = None, lpn_id: int | None = None, batch_id: int | None = None
    ) -> Decimal:
        balances = await self._repo.list_all()
        total = Decimal("0")
        for b in balances:
            if b.product_id != product_id:
                continue
            if location_id and b.location_id != location_id:
                continue
            if lpn_id and b.lpn_id != lpn_id:
                continue
            if batch_id and b.batch_id != batch_id:
                continue
            total += b.quantity - b.reserved_quantity
        return total

    async def add_stock(
        self, *, user_id: int, product_id: int, location_id: int, quantity: Decimal,
        lpn_id: int | None = None, batch_id: int | None = None, document_id: int | None = None,
    ) -> StockBalance:
        if quantity <= 0:
            raise ValueError("Количество должно быть больше 0")

        balance = await self._repo.get_balance(product_id, location_id, lpn_id, batch_id, for_update=True)

        if balance:
            balance.quantity += quantity
            balance.updated_by_id = user_id
            await self._repo._s.flush()
        else:
            balance = await self._repo.create(
                product_id=product_id,
                location_id=location_id,
                lpn_id=lpn_id,
                batch_id=batch_id,
                quantity=quantity,
                reserved_quantity=Decimal("0"),
            )

        await self._repo.create_movement(
            product_id=product_id,
            document_id=document_id,
            location_id=location_id,
            lpn_id=lpn_id,
            batch_id=batch_id,
            direction="in",
            quantity=quantity,
        )

        return balance

    async def remove_stock(
        self, *, user_id: int, product_id: int, location_id: int, quantity: Decimal,
        lpn_id: int | None = None, batch_id: int | None = None, document_id: int | None = None,
    ) -> StockBalance:
        if quantity <= 0:
            raise ValueError("Количество должно быть больше 0")

        balance = await self._repo.get_balance(product_id, location_id, lpn_id, batch_id, for_update=True)

        if not balance:
            raise ValueError("Нет остатка для списания")

        if balance.quantity < quantity:
            raise ValueError(f"Недостаточно остатка: {balance.quantity} < {quantity}")

        balance.quantity -= quantity
        balance.updated_by_id = user_id
        await self._repo._s.flush()

        await self._repo.create_movement(
            product_id=product_id,
            document_id=document_id,
            location_id=location_id,
            lpn_id=lpn_id,
            batch_id=batch_id,
            direction="out",
            quantity=quantity,
        )

        return balance

    async def move_stock(
        self, *, user_id: int, product_id: int, from_location_id: int, to_location_id: int,
        quantity: Decimal, lpn_id: int | None = None, batch_id: int | None = None, document_id: int | None = None,
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
        self, *, user_id: int, product_id: int, location_id: int, quantity: Decimal,
        lpn_id: int | None = None, batch_id: int | None = None,
    ) -> StockBalance:
        balance = await self._repo.get_balance(product_id, location_id, lpn_id, batch_id, for_update=True)
        if not balance:
            raise ValueError("Нет остатка для резервирования")

        available = balance.quantity - balance.reserved_quantity
        if available < quantity:
            raise ValueError(f"Недостаточно доступного остатка: {available} < {quantity}")

        balance.reserved_quantity += quantity
        balance.updated_by_id = user_id
        await self._repo._s.flush()
        return balance

    async def unreserve(
        self, *, user_id: int, product_id: int, location_id: int, quantity: Decimal,
        lpn_id: int | None = None, batch_id: int | None = None,
    ) -> StockBalance:
        balance = await self._repo.get_balance(product_id, location_id, lpn_id, batch_id, for_update=True)
        if not balance:
            raise ValueError("Нет остатка для отмены резервирования")

        if balance.reserved_quantity < quantity:
            raise ValueError("Недостаточно зарезервированного")

        balance.reserved_quantity -= quantity
        balance.updated_by_id = user_id
        await self._repo._s.flush()
        return balance
