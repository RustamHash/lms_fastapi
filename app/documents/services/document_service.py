"""Сервис документов."""

from __future__ import annotations

from decimal import Decimal

import logging

from app.documents.repository import DocumentLineRepository, DocumentRepository

logger = logging.getLogger(__name__)


class DocumentService:
    def __init__(self, doc_repo: DocumentRepository, line_repo: DocumentLineRepository) -> None:
        self._docs = doc_repo
        self._lines = line_repo

    async def create(self, *, user_id: int, **kwargs) -> object:
        logger.info("Создание документа: %s", kwargs.get("document_number"))
        doc = await self._docs.create(
            **kwargs,
        )
        logger.info("Документ создан: id=%s", doc.id)
        return doc

    async def get_by_id(self, document_id: int):
        return await self._docs.get_by_id(document_id)

    async def add_line(self, *, user_id: int, document_id: int, product_id: int, quantity: Decimal, batch_id: int | None = None):
        if quantity <= 0:
            raise ValueError("Количество должно быть больше 0")

        return await self._lines.create(
            document_id=document_id,
            product_id=product_id,
            batch_id=batch_id,
            quantity=quantity,
        )

    async def list_lines(self, document_id: int):
        return await self._lines.list_by_document(document_id)

    async def set_status(self, *, user_id: int, document_id: int, status: str):
        return await self._docs.update(document_id, status=status)

    async def start(self, *, user_id: int, document_id: int):
        return await self.set_status(user_id=user_id, document_id=document_id, status="in_progress")

    async def complete(self, *, user_id: int, document_id: int):
        return await self.set_status(user_id=user_id, document_id=document_id, status="completed")

    async def cancel(self, *, user_id: int, document_id: int):
        return await self.set_status(user_id=user_id, document_id=document_id, status="cancelled")

    async def list_all(self):
        return await self._docs.list_all()

    async def list_by_type(self, document_type: str):
        return await self._docs.list_by_type(document_type)

    async def delete(self, user_id: int, document_id: int) -> bool:
        doc = await self.get_by_id(document_id)
        if doc is None:
            return False
        doc.soft_delete(user_id)
        await self._docs._s.flush()
        return True
