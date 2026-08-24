"""Схемы для топологии склада."""

from __future__ import annotations

from pydantic import BaseModel, Field

from app.api.v1.base_schemas import BaseRead


class WarehouseRead(BaseRead):
    name: str = Field(..., title="Название")
    address_id: int | None = Field(
        None,
        title="Адрес",
        json_schema_extra={"ui_type": "select", "endpoint": "/api/v1/addresses"},
    )


class WarehouseCreate(BaseModel):
    name: str = Field(..., title="Название", min_length=1, max_length=255)
    address_id: int | None = Field(
        None,
        title="Адрес",
        json_schema_extra={"ui_type": "select", "endpoint": "/api/v1/addresses"},
    )


class VirtualWarehouseRead(BaseRead):
    depositor_id: int = Field(
        ...,
        title="Поклажедатель",
        json_schema_extra={"ui_type": "select", "endpoint": "/api/v1/depositors"},
    )
    warehouse_id: int = Field(
        ...,
        title="Физический склад",
        json_schema_extra={"ui_type": "select", "endpoint": "/api/v1/warehouse/topology/warehouses"},
    )
    code: str = Field(..., title="Код")
    name: str = Field(..., title="Наименование")


class VirtualWarehouseCreate(BaseModel):
    depositor_id: int = Field(
        ...,
        title="Поклажедатель",
        json_schema_extra={"ui_type": "select", "endpoint": "/api/v1/depositors"},
    )
    warehouse_id: int = Field(
        ...,
        title="Физический склад",
        json_schema_extra={"ui_type": "select", "endpoint": "/api/v1/warehouse/topology/warehouses"},
    )
    code: str = Field(..., title="Код", min_length=1, max_length=50)
    name: str = Field(..., title="Наименование", min_length=1, max_length=255)


class ZoneRead(BaseRead):
    warehouse_id: int = Field(
        ...,
        title="Склад",
        json_schema_extra={"ui_type": "select", "endpoint": "/api/v1/warehouse/topology/warehouses"},
    )
    name: str = Field(..., title="Название")
    zone_type: str = Field(..., title="Тип зоны")


class ZoneCreate(BaseModel):
    warehouse_id: int = Field(
        ...,
        title="Склад",
        json_schema_extra={"ui_type": "select", "endpoint": "/api/v1/warehouse/topology/warehouses"},
    )
    name: str = Field(..., title="Название")
    zone_type: str = Field(..., title="Тип зоны")


class RowRead(BaseRead):
    zone_id: int = Field(
        ...,
        title="Зона",
        json_schema_extra={"ui_type": "select", "endpoint": "/api/v1/warehouse/topology/zones"},
    )
    code: str = Field(..., title="Код ряда")
    row_type: str = Field(..., title="Тип ряда")


class RowCreate(BaseModel):
    zone_id: int = Field(
        ...,
        title="Зона",
        json_schema_extra={"ui_type": "select", "endpoint": "/api/v1/warehouse/topology/zones"},
    )
    code: str = Field(..., title="Код ряда", min_length=1, max_length=10)
    row_type: str = Field(..., title="Тип ряда", min_length=1, max_length=20)


class LocationRead(BaseRead):
    row_id: int = Field(
        ...,
        title="Ряд",
        json_schema_extra={"ui_type": "select", "endpoint": "/api/v1/warehouse/topology/rows"},
    )
    position: int = Field(..., title="Позиция")
    level: int = Field(1, title="Ярус")
    max_weight: float | None = Field(None, title="Макс. вес")
    max_volume: float | None = Field(None, title="Макс. объём")


class LocationCreate(BaseModel):
    row_id: int = Field(
        ...,
        title="Ряд",
        json_schema_extra={"ui_type": "select", "endpoint": "/api/v1/warehouse/topology/rows"},
    )
    position: int = Field(..., title="Позиция")
    level: int = Field(1, title="Ярус")
    max_weight: float | None = Field(None, title="Макс. вес")
    max_volume: float | None = Field(None, title="Макс. объём")
