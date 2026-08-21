"""Сервис документов."""

from __future__ import annotations

from decimal import Decimal

import logging

from sqlalchemy import select

logger = logging.getLogger(__name__)
from sqlalchemy.ext.asyncio import AsyncSession

from app.documents.models import Document, DocumentLine


class DocumentService:
    def __init__(self, session: AsyncSession) -> None:
        self._s = session

    async def create(
        self,
        *,
        user_id: int,
        document_type: str,
        warehouse_id: int,
        document_number: str,
        document_date=None,
        delivery_date=None,
        contract_id: int | None = None,
        virtual_warehouse_id: int | None = None,
        is_delivery: bool = False,
        is_edo: bool = False,
    ) -> Document:
        logger.info("Создание документа: %s", document_number)
        doc = Document(
            document_type=document_type,
            warehouse_id=warehouse_id,
            document_number=document_number,
            document_date=document_date,
            delivery_date=delivery_date,
            contract_id=contract_id,
            virtual_warehouse_id=virtual_warehouse_id,
            is_delivery=is_delivery,
            is_edo=is_edo,
            created_by_id=user_id,
            updated_by_id=user_id,
        )
        self._s.add(doc)
        await self._s.flush()
        logger.info("Документ создан: id=%s", doc.id)
        return doc

    async def get_by_id(self, document_id: int) -> Document | None:
        return await self._s.get(Document, document_id)

    async def add_line(
        self,
        *,
        user_id: int,
        document_id: int,
        product_id: int,
        quantity: Decimal,
        batch_id: int | None = None,
    ) -> DocumentLine:
        if quantity <= 0:
            raise ValueError("Количество должно быть больше 0")

        line = DocumentLine(
            document_id=document_id,
            product_id=product_id,
            batch_id=batch_id,
            quantity=quantity,
            created_by_id=user_id,
            updated_by_id=user_id,
        )
        self._s.add(line)
        await self._s.flush()
        return line

    async def set_status(self, *, user_id: int, document_id: int, status: str) -> Document | None:
        doc = await self._s.get(Document, document_id)
        if doc is None:
            return None
        doc.status = status
        doc.updated_by_id = user_id
        await self._s.flush()
        return doc

    async def start(self, *, user_id: int, document_id: int) -> Document | None:
        return await self.set_status(user_id=user_id, document_id=document_id, status="in_progress")

    async def complete(self, *, user_id: int, document_id: int) -> Document | None:
        return await self.set_status(user_id=user_id, document_id=document_id, status="completed")

    async def cancel(self, *, user_id: int, document_id: int) -> Document | None:
        return await self.set_status(user_id=user_id, document_id=document_id, status="cancelled")

    async def list_all(self) -> list[Document]:
        stmt = select(Document).where(Document.is_deleted.is_(False)).order_by(Document.created_at.desc())
        return list(await self._s.scalars(stmt))

    async def list_by_type(self, document_type: str) -> list[Document]:
        stmt = (
            select(Document)
            .where(Document.document_type == document_type, Document.is_deleted.is_(False))
            .order_by(Document.created_at.desc())
        )
        return list(await self._s.scalars(stmt))
