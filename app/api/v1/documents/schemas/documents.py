"""Схемы для документов."""

from __future__ import annotations

from datetime import date
from decimal import Decimal

from pydantic import BaseModel, Field

from app.api.v1.base_schemas import BaseRead
from app.core.statuses import DocumentStatus


class DocumentRead(BaseRead):
    document_number: str = Field(..., title="Номер документа")
    document_date: date | None = Field(None, title="Дата документа")
    delivery_date: date | None = Field(None, title="Дата доставки")
    document_type: str = Field(..., title="Тип документа")
    contract_id: int | None = Field(
        None,
        title="Договор",
        json_schema_extra={"ui_type": "select", "endpoint": "/api/v1/contracts"},
    )
    warehouse_id: int = Field(
        ...,
        title="Склад",
        json_schema_extra={"ui_type": "select", "endpoint": "/api/v1/warehouse/topology/warehouses"},
    )
    virtual_warehouse_id: int | None = Field(
        None,
        title="Виртуальный склад",
        json_schema_extra={"ui_type": "select", "endpoint": "/api/v1/warehouse/topology/virtual-warehouses"},
    )
    status: str = Field(DocumentStatus.DRAFT.value, title="Статус")
    is_delivery: bool = Field(False, title="Признак доставки")
    is_edo: bool = Field(False, title="Признак ЭДО")


class DocumentCreate(BaseModel):
    document_type: str = Field(..., title="Тип документа")
    warehouse_id: int = Field(
        ...,
        title="Склад",
        json_schema_extra={"ui_type": "select", "endpoint": "/api/v1/warehouse/topology/warehouses"},
    )
    document_number: str = Field(..., title="Номер документа")
    document_date: date | None = Field(None, title="Дата документа")
    delivery_date: date | None = Field(None, title="Дата доставки")
    contract_id: int | None = Field(
        None,
        title="Договор",
        json_schema_extra={"ui_type": "select", "endpoint": "/api/v1/contracts"},
    )
    virtual_warehouse_id: int | None = Field(None, title="Виртуальный склад")
    is_delivery: bool = Field(False, title="Признак доставки")
    is_edo: bool = Field(False, title="Признак ЭДО")


class DocumentLineRead(BaseRead):
    document_id: int = Field(..., title="Документ")
    product_id: int = Field(..., title="Товар")
    batch_id: int | None = Field(None, title="Партия")
    quantity: Decimal = Field(..., title="Количество")
    processed_quantity: Decimal = Field(Decimal("0"), title="Обработано")


class DocumentLineCreate(BaseModel):
    document_id: int = Field(..., title="Документ")
    product_id: int = Field(
        ...,
        title="Товар",
        json_schema_extra={"ui_type": "select", "endpoint": "/api/v1/warehouse/products"},
    )
    quantity: Decimal = Field(..., title="Количество")
    batch_id: int | None = Field(
        None,
        title="Партия",
        json_schema_extra={"ui_type": "select", "endpoint": "/api/v1/warehouse/batches"},
    )
