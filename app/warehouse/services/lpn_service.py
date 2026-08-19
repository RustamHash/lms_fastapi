"""Сервис LPN."""

from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.warehouse.models import LPN


class LPNService:
    def __init__(self, session: AsyncSession) -> None:
        self._s = session

    async def create(self, *, user_id: int, status: str = "created") -> LPN:
        lpn = LPN(
            status=status,
            created_by_id=user_id,
            updated_by_id=user_id,
        )
        self._s.add(lpn)
        await self._s.flush()
        return lpn

    async def get_by_number(self, number: str) -> LPN | None:
        stmt = select(LPN).where(LPN.number == number)
        return await self._s.scalar(stmt)

    async def set_status(self, *, user_id: int, lpn: LPN, status: str) -> LPN:
        lpn.status = status
        lpn.updated_by_id = user_id
        await self._s.flush()
        return lpn

    async def close(self, *, user_id: int, lpn: LPN) -> LPN:
        return await self.set_status(user_id=user_id, lpn=lpn, status="closed")

    async def ship(self, *, user_id: int, lpn: LPN) -> LPN:
        return await self.set_status(user_id=user_id, lpn=lpn, status="shipped")
