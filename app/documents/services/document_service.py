"""Сервис документов."""

from __future__ import annotations

from decimal import Decimal

from app.documents.models import Document, DocumentLine
from app.documents.repository import DocumentLineRepository, DocumentRepository
from app.warehouse.repository import StockRepository
from app.warehouse.services.plan_fact_view import (
    discrepancy_kind,
    movement_row,
    product_label,
)


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

    async def plan_fact(self, document_id: int, stock_repo: StockRepository) -> dict:
        """План (строки документа), факт (движения) и сверка."""
        lines = await self._lines.list_by_document(document_id)
        movements = await stock_repo.list_movements_for_document(document_id)
        plan = [
            {
                "id": line.id,
                "product_id": line.product_id,
                **product_label(line.product),
                "quantity": line.quantity,
                "batch_number": line.batch.batch_number if line.batch else "",
                "manufacture_date": line.batch.production_date if line.batch else None,
            }
            for line in lines
        ]
        fact = [movement_row(move) for move in movements]
        discrepancies = []
        for line in lines:
            planned = line.quantity
            fact_qty = line.processed_quantity
            discrepancies.append(
                {
                    "inbound_order_line_id": None,
                    "product_id": line.product_id,
                    **product_label(line.product),
                    "qty_planned": planned,
                    "qty_fact": fact_qty,
                    "qty_diff": fact_qty - planned,
                    "kind": discrepancy_kind(planned, fact_qty),
                }
            )
        return {"plan": plan, "fact": fact, "discrepancies": discrepancies}
