"""Инвариант остатка: unique ключ, гонка, LPN обязателен."""

from __future__ import annotations

import asyncio
from decimal import Decimal

import pytest
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import BadRequestError
from app.warehouse.models import StockBalance, StockMovement
from app.warehouse.repository import StockRepository
from app.warehouse.services.stock_service import StockService


def _service(session: AsyncSession) -> StockService:
    return StockService(StockRepository(session))


async def test_race_two_adds_one_row(session_factory, stock_ctx, session: AsyncSession) -> None:
    await session.commit()
    ctx = stock_ctx

    async def add_qty(qty: Decimal) -> None:
        async with session_factory() as other:
            async with other.begin():
                await _service(other).add_stock(
                    user_id=ctx["user_id"],
                    product_id=ctx["product_id"],
                    location_id=ctx["location_id"],
                    quantity=qty,
                    lpn_id=ctx["lpn_id"],
                    batch_id=ctx["batch_id"],
                )

    await asyncio.gather(add_qty(Decimal("2")), add_qty(Decimal("3")))

    async with session_factory() as check:
        count = await check.scalar(
            select(func.count()).select_from(StockBalance).where(
                StockBalance.product_id == ctx["product_id"],
                StockBalance.location_id == ctx["location_id"],
                StockBalance.lpn_id == ctx["lpn_id"],
                StockBalance.batch_id == ctx["batch_id"],
            )
        )
        qty = await check.scalar(
            select(StockBalance.quantity).where(
                StockBalance.product_id == ctx["product_id"],
                StockBalance.location_id == ctx["location_id"],
                StockBalance.lpn_id == ctx["lpn_id"],
                StockBalance.batch_id == ctx["batch_id"],
            )
        )
    assert count == 1
    assert qty == Decimal("5")


async def test_two_lpns_are_two_rows(session: AsyncSession, stock_ctx: dict) -> None:
    svc = _service(session)
    await svc.add_stock(
        user_id=stock_ctx["user_id"],
        product_id=stock_ctx["product_id"],
        location_id=stock_ctx["location_id"],
        quantity=Decimal("4"),
        lpn_id=stock_ctx["lpn_id"],
        batch_id=stock_ctx["batch_id"],
    )
    await svc.add_stock(
        user_id=stock_ctx["user_id"],
        product_id=stock_ctx["product_id"],
        location_id=stock_ctx["location_id"],
        quantity=Decimal("7"),
        lpn_id=stock_ctx["lpn_b_id"],
        batch_id=stock_ctx["batch_id"],
    )
    await svc.move_stock(
        user_id=stock_ctx["user_id"],
        product_id=stock_ctx["product_id"],
        from_location_id=stock_ctx["location_id"],
        to_location_id=stock_ctx["location_b_id"],
        quantity=Decimal("4"),
        lpn_id=stock_ctx["lpn_id"],
        batch_id=stock_ctx["batch_id"],
    )
    left = await svc.get_balance(
        stock_ctx["product_id"],
        stock_ctx["location_id"],
        stock_ctx["lpn_b_id"],
        stock_ctx["batch_id"],
    )
    moved = await svc.get_balance(
        stock_ctx["product_id"],
        stock_ctx["location_b_id"],
        stock_ctx["lpn_id"],
        stock_ctx["batch_id"],
    )
    gone = await svc.get_balance(
        stock_ctx["product_id"],
        stock_ctx["location_id"],
        stock_ctx["lpn_id"],
        stock_ctx["batch_id"],
    )
    assert left is not None and left.quantity == Decimal("7")
    assert moved is not None and moved.quantity == Decimal("4")
    assert gone is not None and gone.quantity == Decimal("0")


async def test_add_without_lpn_or_batch_errors(session: AsyncSession, stock_ctx: dict) -> None:
    svc = _service(session)
    with pytest.raises(BadRequestError, match="LPN"):
        await svc.add_stock(
            user_id=stock_ctx["user_id"],
            product_id=stock_ctx["product_id"],
            location_id=stock_ctx["location_id"],
            quantity=Decimal("1"),
            lpn_id=None,
            batch_id=stock_ctx["batch_id"],
        )
    with pytest.raises(BadRequestError, match="парти"):
        await svc.add_stock(
            user_id=stock_ctx["user_id"],
            product_id=stock_ctx["product_id"],
            location_id=stock_ctx["location_id"],
            quantity=Decimal("1"),
            lpn_id=stock_ctx["lpn_id"],
            batch_id=None,
        )
    rows = await session.scalar(
        select(func.count()).select_from(StockBalance).where(
            StockBalance.product_id == stock_ctx["product_id"]
        )
    )
    assert rows == 0


async def test_remove_below_zero_keeps_quantity(session: AsyncSession, stock_ctx: dict) -> None:
    svc = _service(session)
    await svc.add_stock(
        user_id=stock_ctx["user_id"],
        product_id=stock_ctx["product_id"],
        location_id=stock_ctx["location_id"],
        quantity=Decimal("5"),
        lpn_id=stock_ctx["lpn_id"],
        batch_id=stock_ctx["batch_id"],
    )
    with pytest.raises(BadRequestError, match="Недостаточно"):
        await svc.remove_stock(
            user_id=stock_ctx["user_id"],
            product_id=stock_ctx["product_id"],
            location_id=stock_ctx["location_id"],
            quantity=Decimal("9"),
            lpn_id=stock_ctx["lpn_id"],
            batch_id=stock_ctx["batch_id"],
        )
    balance = await svc.get_balance(
        stock_ctx["product_id"],
        stock_ctx["location_id"],
        stock_ctx["lpn_id"],
        stock_ctx["batch_id"],
    )
    assert balance is not None and balance.quantity == Decimal("5")


async def test_move_writes_two_movements(session: AsyncSession, stock_ctx: dict) -> None:
    svc = _service(session)
    await svc.add_stock(
        user_id=stock_ctx["user_id"],
        product_id=stock_ctx["product_id"],
        location_id=stock_ctx["location_id"],
        quantity=Decimal("6"),
        lpn_id=stock_ctx["lpn_id"],
        batch_id=stock_ctx["batch_id"],
    )
    await svc.move_stock(
        user_id=stock_ctx["user_id"],
        product_id=stock_ctx["product_id"],
        from_location_id=stock_ctx["location_id"],
        to_location_id=stock_ctx["location_b_id"],
        quantity=Decimal("2"),
        lpn_id=stock_ctx["lpn_id"],
        batch_id=stock_ctx["batch_id"],
    )
    src = await svc.get_balance(
        stock_ctx["product_id"],
        stock_ctx["location_id"],
        stock_ctx["lpn_id"],
        stock_ctx["batch_id"],
    )
    dst = await svc.get_balance(
        stock_ctx["product_id"],
        stock_ctx["location_b_id"],
        stock_ctx["lpn_id"],
        stock_ctx["batch_id"],
    )
    assert src is not None and src.quantity == Decimal("4")
    assert dst is not None and dst.quantity == Decimal("2")

    movements = list(
        await session.scalars(
            select(StockMovement).where(StockMovement.product_id == stock_ctx["product_id"])
        )
    )
    assert len(movements) == 3
    assert all(m.moved_at is not None for m in movements)
    assert all(m.moved_by_id == stock_ctx["user_id"] for m in movements)
    directions = sorted(m.direction for m in movements)
    assert directions == ["in", "in", "out"]
