"""Базовый репозиторий с CRUD операциями."""

from __future__ import annotations

from typing import Any, Generic, TypeVar

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.infrastructure.orm_base import Base

ModelType = TypeVar("ModelType", bound=Base)


class BaseRepository(Generic[ModelType]):
    """Универсальный репозиторий."""

    def __init__(self, session: AsyncSession, model: type[ModelType]) -> None:
        self._s = session
        self._model = model

    async def get_by_id(self, id: int) -> ModelType | None:
        return await self._s.get(self._model, id)

    async def list_all(self) -> list[ModelType]:
        stmt = select(self._model)
        return list(await self._s.scalars(stmt))

    async def create(self, **kwargs: Any) -> ModelType:
        row = self._model(**kwargs)
        self._s.add(row)
        await self._s.flush()
        await self._s.refresh(row)
        return row

    async def update(self, id: int, **kwargs: Any) -> ModelType | None:
        row = await self.get_by_id(id)
        if row is None:
            return None
        for field, value in kwargs.items():
            setattr(row, field, value)
        await self._s.flush()
        await self._s.refresh(row)
        return row

    async def soft_delete(self, id: int, user_id: int | None = None) -> bool:
        row = await self.get_by_id(id)
        if row is None:
            return False
        row.soft_delete(user_id)
        await self._s.flush()
        return True
