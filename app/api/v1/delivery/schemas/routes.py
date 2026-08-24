"""Схемы для маршрутов."""

from __future__ import annotations

from datetime import date as date_type

from pydantic import BaseModel, Field

from app.api.v1.base_schemas import BaseRead


class RouteRead(BaseRead):
    number: str = Field(..., title="Номер")
    driver_id: int = Field(
        ...,
        title="Водитель",
        json_schema_extra={"ui_type": "select", "endpoint": "/api/v1/delivery/drivers"},
    )
    vehicle_id: int = Field(
        ...,
        title="Автомобиль",
        json_schema_extra={"ui_type": "select", "endpoint": "/api/v1/delivery/vehicles"},
    )
    route_date: date_type = Field(..., title="Дата")
    status: str = Field("planned", title="Статус")


class RouteCreate(BaseModel):
    number: str = Field(..., title="Номер")
    driver_id: int = Field(
        ...,
        title="Водитель",
        json_schema_extra={"ui_type": "select", "endpoint": "/api/v1/delivery/drivers"},
    )
    vehicle_id: int = Field(
        ...,
        title="Автомобиль",
        json_schema_extra={"ui_type": "select", "endpoint": "/api/v1/delivery/vehicles"},
    )
    route_date: date_type = Field(..., title="Дата")
