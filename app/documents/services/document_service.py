"""Сервис документов."""

from __future__ import annotations

from decimal import Decimal

from app.documents.models import Document, DocumentLine
from app.documents.repository import DocumentLineRepository, DocumentRepository


class DocumentService:
    def __init__(self, doc_repo: DocumentRepository, line_repo: DocumentLineRepository) -> None:
        self._docs = doc_repo
        self._lines = line_repo

    async def get_by_id(self, document_id: int) -> Document | None:
        return await self._docs.get_by_id(document_id)

    async def list_all(self) -> list[Document]:
        return await self._docs.list_all()

    async def list_by_type(self, document_type: str) -> list[Document]:
        return await self._docs.list_by_type(document_type)

    async def create(self, *, user_id: int | None = None, **kwargs) -> Document:
        return await self._docs.create(**kwargs)

    async def update(self, document_id: int, user_id: int | None = None, **kwargs) -> Document | None:
        return await self._docs.update(document_id, **kwargs)

    async def soft_delete(self, document_id: int, user_id: int | None = None) -> bool:
        return await self._docs.soft_delete(document_id, user_id)

    async def add_line(
        self, *, user_id: int, document_id: int, product_id: int, quantity: Decimal, batch_id: int | None = None
    ) -> DocumentLine:
        if quantity <= 0:
            raise ValueError("Количество должно быть больше 0")
        return await self._lines.create(
            document_id=document_id,
            product_id=product_id,
            batch_id=batch_id,
            quantity=quantity,
        )

    async def list_lines(self, document_id: int) -> list[DocumentLine]:
        return await self._lines.list_by_document(document_id)

    async def set_status(self, *, user_id: int, document_id: int, status: str) -> Document | None:
        return await self._docs.update(document_id, status=status)
