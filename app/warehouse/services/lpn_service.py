"""Сервис LPN."""

from __future__ import annotations

import uuid

from app.warehouse.repository import LPNRepository


class LPNService:
    def __init__(self, repo: LPNRepository) -> None:
        self._repo = repo

    async def create(self, *, user_id: int, status: str = "created"):
        # Генерируем номер
        number = f"LPN{uuid.uuid4().hex[:12].upper()}"

        return await self._repo.create(
            number=number,
            status=status,
        )

    async def get_by_number(self, number: str):
        return await self._repo.get_by_number(number)

    async def set_status(self, *, user_id: int, lpn_id: int, status: str):
        return await self._repo.update(lpn_id, status=status)

    async def close(self, *, user_id: int, lpn_id: int):
        return await self.set_status(user_id=user_id, lpn_id=lpn_id, status="closed")

    async def ship(self, *, user_id: int, lpn_id: int):
        return await self.set_status(user_id=user_id, lpn_id=lpn_id, status="shipped")
