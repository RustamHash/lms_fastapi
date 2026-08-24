"""Схемы для партий."""

from __future__ import annotations

from datetime import date

from pydantic import BaseModel, Field

from app.api.v1.base_schemas import BaseRead


class BatchRead(BaseRead):
    product_id: int = Field(
        ...,
        title="Товар",
        json_schema_extra={"ui_type": "select", "endpoint": "/api/v1/warehouse/products"},
    )
    batch_number: str = Field(..., title="Номер партии")
    production_date: date | None = Field(None, title="Дата производства")
    expiration_date: date | None = Field(None, title="Срок годности")


class BatchCreate(BaseModel):
    product_id: int = Field(
        ...,
        title="Товар",
        json_schema_extra={"ui_type": "select", "endpoint": "/api/v1/warehouse/products"},
    )
    batch_number: str | None = Field(None, title="Номер партии")
    production_date: date | None = Field(None, title="Дата производства")
    expiration_date: date | None = Field(None, title="Срок годности")
