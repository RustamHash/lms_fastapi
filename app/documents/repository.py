# app/documents/repository.py

"""Репозитории для модуля documents."""

from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from app.documents.models import Document, DocumentLine


class DocumentRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._s = session

    async def get_by_id(self, id: int) -> Document | None:
        row = await self._s.get(Document, id)
        if row is None or row.is_deleted:
            return None
        return row

    async def list_all(self) -> list[Document]:
        stmt = select(Document).where(Document.is_deleted.is_(False))
        return list(await self._s.scalars(stmt))

    async def list_by_type(self, document_type: str) -> list[Document]:
        stmt = select(Document).where(
            Document.document_type == document_type,
            Document.is_deleted.is_(False),
        )
        return list(await self._s.scalars(stmt))

    async def create(self, **kwargs) -> Document:
        row = Document(**kwargs)
        self._s.add(row)
        await self._s.flush()
        return row

    async def update(self, id: int, **kwargs) -> Document | None:
        row = await self.get_by_id(id)
        if row is None:
            return None
        for field, value in kwargs.items():
            setattr(row, field, value)
        await self._s.flush()
        return row

    async def soft_delete(self, id: int, user_id: int | None = None) -> bool:
        row = await self.get_by_id(id)
        if row is None:
            return False
        row.soft_delete(user_id)
        await self._s.flush()
        return True


class DocumentLineRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._s = session

    async def get_by_id(self, id: int) -> DocumentLine | None:
        return await self._s.get(DocumentLine, id)

    async def list_all(self) -> list[DocumentLine]:
        return list(await self._s.scalars(select(DocumentLine)))

    async def list_by_document(self, document_id: int) -> list[DocumentLine]:
        stmt = (
            select(DocumentLine)
            .options(
                selectinload(DocumentLine.product),
                selectinload(DocumentLine.batch),
            )
            .where(
                DocumentLine.document_id == document_id,
                DocumentLine.is_deleted.is_(False),
            )
        )
        return list(await self._s.scalars(stmt))

    async def create(self, **kwargs) -> DocumentLine:
        row = DocumentLine(**kwargs)
        self._s.add(row)
        await self._s.flush()
        return row

    async def update(self, id: int, **kwargs) -> DocumentLine | None:
        row = await self._s.get(DocumentLine, id)
        if row is None:
            return None
        for field, value in kwargs.items():
            setattr(row, field, value)
        await self._s.flush()
        return row

    async def soft_delete(self, id: int, user_id: int | None = None) -> bool:
        row = await self._s.get(DocumentLine, id)
        if row is None:
            return False
        row.soft_delete(user_id)
        await self._s.flush()
        return True
