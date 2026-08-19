"""Схемы для модуля warehouse."""

from __future__ import annotations

from datetime import date
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


# ========== Топология ==========

class WarehouseRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    address_id: int | None = None


class WarehouseCreate(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    address_id: int | None = None


class ZoneRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    warehouse_id: int
    name: str
    zone_type: str


class ZoneCreate(BaseModel):
    warehouse_id: int
    name: str
    zone_type: str


class LocationRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    row_id: int
    position: int
    level: int = 1
    max_weight: float | None = None
    max_volume: float | None = None


# ========== Товары ==========

class ProductRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
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


# ========== Партии ==========

class BatchRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    product_id: int
    batch_number: str
    production_date: date | None = None
    expiration_date: date | None = None


class BatchCreate(BaseModel):
    product_id: int
    batch_number: str | None = None
    production_date: date | None = None
    expiration_date: date | None = None


# ========== LPN ==========

class LPNRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    number: str
    status: str


class LPNCreate(BaseModel):
    status: str = "created"


# ========== Остатки ==========

class StockBalanceRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
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


class StockReserve(BaseModel):
    product_id: int
    location_id: int
    quantity: Decimal
    lpn_id: int | None = None
    batch_id: int | None = None


# ========== Задания ==========

class TaskRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
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
