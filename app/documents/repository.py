"""Репозитории для модуля documents."""

from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.documents.models import Document, DocumentLine


class DocumentRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._s = session

    async def get_by_id(self, document_id: int) -> Document | None:
        return await self._s.get(Document, document_id)

    async def list_all(self) -> list[Document]:
        stmt = select(Document).order_by(Document.created_at.desc())
        return list(await self._s.scalars(stmt))

    async def list_by_type(self, document_type: str) -> list[Document]:
        stmt = select(Document).where(Document.document_type == document_type)
        return list(await self._s.scalars(stmt))

    async def create(self, **kwargs) -> Document:
        doc = Document(**kwargs)
        self._s.add(doc)
        await self._s.flush()
        return doc

    async def update(self, document_id: int, **kwargs) -> Document | None:
        doc = await self.get_by_id(document_id)
        if doc is None:
            return None
        for field, value in kwargs.items():
            setattr(doc, field, value)
        await self._s.flush()
        return doc

    async def delete(self, document_id: int) -> bool:
        doc = await self.get_by_id(document_id)
        if doc is None:
            return False
        await self._s.delete(doc)
        await self._s.flush()
        return True


class DocumentLineRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._s = session

    async def get_by_id(self, line_id: int) -> DocumentLine | None:
        return await self._s.get(DocumentLine, line_id)

    async def list_by_document(self, document_id: int) -> list[DocumentLine]:
        stmt = select(DocumentLine).where(DocumentLine.document_id == document_id)
        return list(await self._s.scalars(stmt))

    async def create(self, **kwargs) -> DocumentLine:
        line = DocumentLine(**kwargs)
        self._s.add(line)
        await self._s.flush()
        return line

    async def update(self, line_id: int, **kwargs) -> DocumentLine | None:
        line = await self.get_by_id(line_id)
        if line is None:
            return None
        for field, value in kwargs.items():
            setattr(line, field, value)
        await self._s.flush()
        return line

    async def delete(self, line_id: int) -> bool:
        line = await self.get_by_id(line_id)
        if line is None:
            return False
        await self._s.delete(line)
        await self._s.flush()
        return True
