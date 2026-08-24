"""Схемы для водителей."""

from __future__ import annotations

from pydantic import BaseModel, Field

from app.api.v1.base_schemas import BaseRead


class DriverRead(BaseRead):
    name: str = Field(..., title="ФИО")
    phone: str = Field("", title="Телефон")
    carrier_id: int | None = Field(
        None,
        title="Перевозчик",
        json_schema_extra={"ui_type": "select", "endpoint": "/api/v1/carriers"},
    )


class DriverCreate(BaseModel):
    name: str = Field(..., title="ФИО")
    phone: str = Field("", title="Телефон")
    carrier_id: int | None = Field(
        None,
        title="Перевозчик",
        json_schema_extra={"ui_type": "select", "endpoint": "/api/v1/carriers"},
    )
