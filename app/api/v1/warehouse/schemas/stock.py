"""Схемы для остатков."""

from __future__ import annotations

from decimal import Decimal

from pydantic import BaseModel, Field

from app.api.v1.base_schemas import BaseRead


class StockBalanceRead(BaseRead):
    product_id: int = Field(
        ...,
        title="Товар",
        json_schema_extra={"ui_type": "select", "endpoint": "/api/v1/warehouse/products"},
    )
    location_id: int = Field(
        ...,
        title="Ячейка",
        json_schema_extra={"ui_type": "select", "endpoint": "/api/v1/warehouse/topology/locations"},
    )
    lpn_id: int = Field(
        ...,
        title="LPN",
        json_schema_extra={"ui_type": "select", "endpoint": "/api/v1/warehouse/lpns"},
    )
    batch_id: int = Field(
        ...,
        title="Партия",
        json_schema_extra={"ui_type": "select", "endpoint": "/api/v1/warehouse/batches"},
    )
    quantity: Decimal = Field(..., title="Количество", ge=0)
    reserved_quantity: Decimal = Field(Decimal("0"), title="Зарезервировано", ge=0)


class StockAdd(BaseModel):
    product_id: int = Field(
        ...,
        title="Товар",
        json_schema_extra={"ui_type": "select", "endpoint": "/api/v1/warehouse/products"},
    )
    location_id: int = Field(
        ...,
        title="Ячейка",
        json_schema_extra={"ui_type": "select", "endpoint": "/api/v1/warehouse/topology/locations"},
    )
    quantity: Decimal = Field(..., title="Количество", gt=0)
    lpn_id: int = Field(
        ...,
        title="LPN",
        json_schema_extra={"ui_type": "select", "endpoint": "/api/v1/warehouse/lpns"},
    )
    batch_id: int = Field(
        ...,
        title="Партия",
        json_schema_extra={"ui_type": "select", "endpoint": "/api/v1/warehouse/batches"},
    )
    document_id: int | None = Field(
        None,
        title="Документ",
        json_schema_extra={"ui_type": "select", "endpoint": "/api/v1/documents"},
    )


class StockRemove(BaseModel):
    product_id: int = Field(
        ...,
        title="Товар",
        json_schema_extra={"ui_type": "select", "endpoint": "/api/v1/warehouse/products"},
    )
    location_id: int = Field(
        ...,
        title="Ячейка",
        json_schema_extra={"ui_type": "select", "endpoint": "/api/v1/warehouse/topology/locations"},
    )
    quantity: Decimal = Field(..., title="Количество", gt=0)
    lpn_id: int = Field(
        ...,
        title="LPN",
        json_schema_extra={"ui_type": "select", "endpoint": "/api/v1/warehouse/lpns"},
    )
    batch_id: int = Field(
        ...,
        title="Партия",
        json_schema_extra={"ui_type": "select", "endpoint": "/api/v1/warehouse/batches"},
    )
    document_id: int | None = Field(
        None,
        title="Документ",
        json_schema_extra={"ui_type": "select", "endpoint": "/api/v1/documents"},
    )


class StockMove(BaseModel):
    product_id: int = Field(
        ...,
        title="Товар",
        json_schema_extra={"ui_type": "select", "endpoint": "/api/v1/warehouse/products"},
    )
    from_location_id: int = Field(
        ...,
        title="Откуда",
        json_schema_extra={"ui_type": "select", "endpoint": "/api/v1/warehouse/topology/locations"},
    )
    to_location_id: int = Field(
        ...,
        title="Куда",
        json_schema_extra={"ui_type": "select", "endpoint": "/api/v1/warehouse/topology/locations"},
    )
    quantity: Decimal = Field(..., title="Количество", gt=0)
    lpn_id: int = Field(
        ...,
        title="LPN",
        json_schema_extra={"ui_type": "select", "endpoint": "/api/v1/warehouse/lpns"},
    )
    batch_id: int = Field(
        ...,
        title="Партия",
        json_schema_extra={"ui_type": "select", "endpoint": "/api/v1/warehouse/batches"},
    )
    document_id: int | None = Field(
        None,
        title="Документ",
        json_schema_extra={"ui_type": "select", "endpoint": "/api/v1/documents"},
    )
