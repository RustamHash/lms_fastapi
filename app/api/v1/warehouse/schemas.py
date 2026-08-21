"""Схемы для модуля warehouse."""

from __future__ import annotations

from datetime import date
from decimal import Decimal

from pydantic import BaseModel, Field

from app.api.v1.base_schemas import BaseRead


class WarehouseRead(BaseRead):
    name: str
    address_id: int | None = None


class WarehouseCreate(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    address_id: int | None = None


class ZoneRead(BaseRead):
    warehouse_id: int
    name: str
    zone_type: str


class ZoneCreate(BaseModel):
    warehouse_id: int
    name: str
    zone_type: str


class LocationRead(BaseRead):
    row_id: int
    position: int
    level: int = 1
    max_weight: float | None = None
    max_volume: float | None = None


class VirtualWarehouseRead(BaseRead):
    depositor_id: int
    warehouse_id: int
    code: str
    name: str


class VirtualWarehouseCreate(BaseModel):
    depositor_id: int
    warehouse_id: int
    code: str = Field(min_length=1, max_length=50)
    name: str = Field(min_length=1, max_length=255)


class RowRead(BaseRead):
    zone_id: int
    code: str
    row_type: str


class RowCreate(BaseModel):
    zone_id: int
    code: str = Field(min_length=1, max_length=10)
    row_type: str = Field(min_length=1, max_length=20)


class LocationCreate(BaseModel):
    row_id: int
    position: int
    level: int = 1
    max_weight: float | None = None
    max_volume: float | None = None


class ProductRead(BaseRead):
    depositor_id: int
    external_id: str
    sku: str = ""
    name: str
    legal_name: str = ""
    weight: Decimal
    volume: Decimal
    price: Decimal | None = None
    shelf_life_days: int | None = None
    min_shelf_life_days: int | None = None
    is_marked: bool = False
    is_serial_tracked: bool = False
    is_batch_tracked: bool = False
    is_expiration_tracked: bool = False
    temperature_requirements: str = ""


class ProductCreate(BaseModel):
    depositor_id: int
    external_id: str = Field(min_length=1, max_length=255)
    name: str = Field(min_length=1, max_length=255)
    sku: str = ""
    legal_name: str = ""
    weight: Decimal = Decimal("0")
    volume: Decimal = Decimal("0")
    price: Decimal | None = None
    shelf_life_days: int | None = None
    min_shelf_life_days: int | None = None
    is_marked: bool = False
    is_serial_tracked: bool = False
    is_batch_tracked: bool = False
    is_expiration_tracked: bool = False
    temperature_requirements: str = ""


class BatchRead(BaseRead):
    product_id: int
    batch_number: str
    production_date: date | None = None
    expiration_date: date | None = None


class BatchCreate(BaseModel):
    product_id: int
    batch_number: str | None = None
    production_date: date | None = None
    expiration_date: date | None = None


class LPNRead(BaseRead):
    number: str
    status: str


class LPNCreate(BaseModel):
    status: str = "created"


class StockBalanceRead(BaseRead):
    product_id: int
    location_id: int
    lpn_id: int | None = None
    batch_id: int
    quantity: Decimal
    reserved_quantity: Decimal = Decimal("0")


class StockAdd(BaseModel):
    product_id: int
    location_id: int
    quantity: Decimal
    lpn_id: int | None = None
    batch_id: int | None = None
    document_id: int | None = None


class StockRemove(BaseModel):
    product_id: int
    location_id: int
    quantity: Decimal
    lpn_id: int | None = None
    batch_id: int | None = None
    document_id: int | None = None


class StockMove(BaseModel):
    product_id: int
    from_location_id: int
    to_location_id: int
    quantity: Decimal
    lpn_id: int | None = None
    batch_id: int | None = None
    document_id: int | None = None


class TaskRead(BaseRead):
    task_type: str
    document_id: int | None = None
    assignee_id: int | None = None
    status: str


class TaskCreate(BaseModel):
    task_type: str
    document_id: int | None = None
    assignee_id: int | None = None


class TaskLineAdd(BaseModel):
    task_id: int
    product_id: int
    plan_qty: int = 0
    from_location_id: int | None = None
    to_location_id: int | None = None
    lpn_id: int | None = None
    batch_id: int | None = None


class TaskComplete(BaseModel):
    force: bool = False


class TaskLineComplete(BaseModel):
    fact_qty: int
    location_id: int | None = None
    to_location_id: int | None = None
    batch_id: int | None = None
