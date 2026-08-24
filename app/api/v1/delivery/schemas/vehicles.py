"""Схемы для автомобилей."""

from __future__ import annotations

from pydantic import BaseModel, Field

from app.api.v1.base_schemas import BaseRead


class VehicleRead(BaseRead):
    number: str = Field(..., title="Гос. номер")
    brand: str = Field("", title="Марка")
    model: str = Field("", title="Модель")
    capacity: float | None = Field(None, title="Грузоподъёмность")
    volume: float | None = Field(None, title="Объём")
    carrier_id: int | None = Field(
        None,
        title="Перевозчик",
        json_schema_extra={"ui_type": "select", "endpoint": "/api/v1/carriers"},
    )


class VehicleCreate(BaseModel):
    number: str = Field(..., title="Гос. номер")
    brand: str = Field("", title="Марка")
    model: str = Field("", title="Модель")
    capacity: float | None = Field(None, title="Грузоподъёмность")
    volume: float | None = Field(None, title="Объём")
    carrier_id: int | None = Field(
        None,
        title="Перевозчик",
        json_schema_extra={"ui_type": "select", "endpoint": "/api/v1/carriers"},
    )
