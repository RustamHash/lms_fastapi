# app/files/repository.py

"""Репозиторий для файлов."""

from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.files.models import File


class FileRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._s = session

    async def get_by_id(self, id: int) -> File | None:
        return await self._s.get(File, id)

    async def list_all(self) -> list[File]:
        stmt = select(File)
        return list(await self._s.scalars(stmt))

    async def create(self, **kwargs) -> File:
        row = File(**kwargs)
        self._s.add(row)
        await self._s.flush()
        return row

    async def update(self, id: int, **kwargs) -> File | None:
        row = await self._s.get(File, id)
        if row is None:
            return None
        for field, value in kwargs.items():
            setattr(row, field, value)
        await self._s.flush()
        return row

    async def soft_delete(self, id: int, user_id: int | None = None) -> bool:
        row = await self._s.get(File, id)
        if row is None:
            return False
        row.soft_delete(user_id)
        await self._s.flush()
        return True
