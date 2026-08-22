"""Схемы для модуля documents."""

from __future__ import annotations

from datetime import date
from decimal import Decimal
from typing import TYPE_CHECKING, Any

from pydantic import BaseModel

from app.api.v1.base_schemas import BaseRead
from app.documents.document_types import DocumentType
from app.core.statuses import DocumentStatus

if TYPE_CHECKING:
    from app.api.v1.warehouse.schemas import WarehouseRead


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


# ========== ENRICHED ==========

class DocumentList(BaseRead):
    """Плоская схема для таблицы документов."""
    document_number: str
    document_type: str
    document_type_label: str = ""
    document_date: date | None = None
    delivery_date: date | None = None
    status: str = "draft"
    status_label: str = ""

    # Плоские связи
    warehouse_name: str | None = None


class DocumentDetail(BaseRead):
    """Вложенная схема для детальной страницы документа."""
    document_number: str
    document_type: str
    document_date: date | None = None
    delivery_date: date | None = None
    status: str = "draft"
    is_delivery: bool = False
    is_edo: bool = False

    # Вложенные
    warehouse: Any | None = None
    lines: list = []
    contract: Any | None = None
    virtual_warehouse: Any | None = None
