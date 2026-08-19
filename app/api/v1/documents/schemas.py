"""Схемы для модуля documents."""

from __future__ import annotations

from datetime import date
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


class DocumentRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    document_number: str
    document_date: date | None = None
    delivery_date: date | None = None
    document_type: str
    contract_id: int | None = None
    trade_point_id: int | None = None
    warehouse_id: int
    virtual_warehouse_id: int | None = None
    status: str
    is_delivery: bool = False
    is_edo: bool = False


class DocumentCreate(BaseModel):
    document_type: str
    warehouse_id: int
    document_number: str
    document_date: date | None = None
    delivery_date: date | None = None
    contract_id: int | None = None
    trade_point_id: int | None = None
    virtual_warehouse_id: int | None = None
    is_delivery: bool = False
    is_edo: bool = False


class DocumentLineRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
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
