"""Схемы для модуля documents."""

from __future__ import annotations

from datetime import date
from decimal import Decimal

from pydantic import BaseModel

from app.api.v1.base_schemas import BaseRead
from app.documents.document_types import DocumentType
from app.core.statuses import DocumentStatus


class DocumentRead(BaseRead):
    document_number: str
    document_date: date | None = None
    delivery_date: date | None = None
    document_type: str
    contract_id: int | None = None
    warehouse_id: int
    virtual_warehouse_id: int | None = None
    status: str = DocumentStatus.DRAFT.value
    is_delivery: bool = False
    is_edo: bool = False


class DocumentCreate(BaseModel):
    document_type: DocumentType
    warehouse_id: int
    document_number: str
    document_date: date | None = None
    delivery_date: date | None = None
    contract_id: int | None = None
    virtual_warehouse_id: int | None = None
    is_delivery: bool = False
    is_edo: bool = False


class DocumentLineRead(BaseRead):
    document_id: int
    product_id: int
    batch_id: int | None = None
    quantity: Decimal
    processed_quantity: Decimal = Decimal("0")


class DocumentLineCreate(BaseModel):
    document_id: int
    product_id: int
    quantity: Decimal
    batch_id: int | None = None


class DocumentStatusUpdate(BaseModel):
    status: str
