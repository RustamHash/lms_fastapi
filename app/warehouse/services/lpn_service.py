"""Сервис LPN."""

from __future__ import annotations

import uuid

from app.warehouse.models import LPN
from app.warehouse.repository import LPNRepository


class LPNService:
    def __init__(self, repo: LPNRepository) -> None:
        self._repo = repo

    async def get_by_id(self, lpn_id: int) -> LPN | None:
        return await self._repo.get_by_id(lpn_id)

    async def get_by_number(self, number: str) -> LPN | None:
        return await self._repo.get_by_number(number)

    async def list_all(self) -> list[LPN]:
        return await self._repo.list_all()

    async def create(self, *, user_id: int | None = None, status: str = "created") -> LPN:
        number = f"LPN{uuid.uuid4().hex[:12].upper()}"
        return await self._repo.create(number=number, status=status)

    async def update(self, lpn_id: int, user_id: int | None = None, **kwargs) -> LPN | None:
        return await self._repo.update(lpn_id, **kwargs)

    async def soft_delete(self, lpn_id: int, user_id: int | None = None) -> bool:
        return await self._repo.soft_delete(lpn_id, user_id)
