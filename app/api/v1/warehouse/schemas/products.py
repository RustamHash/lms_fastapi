"""Схемы для товаров, групп, упаковок."""

from __future__ import annotations

from decimal import Decimal

from pydantic import BaseModel, Field

from app.api.v1.base_schemas import BaseRead


class ProductRead(BaseRead):
    depositor_id: int = Field(
        ...,
        title="Поклажедатель",
        json_schema_extra={"ui_type": "select", "endpoint": "/api/v1/depositors"},
    )
    external_id: str = Field(..., title="Внешний код")
    sku: str = Field("", title="Артикул")
    name: str = Field(..., title="Наименование")
    legal_name: str = Field("", title="Полное наименование")
    weight: Decimal = Field(..., title="Вес нетто")
    volume: Decimal = Field(..., title="Объём")
    price: Decimal | None = Field(None, title="Цена")
    shelf_life_days: int | None = Field(None, title="Срок годности (дней)")
    min_shelf_life_days: int | None = Field(None, title="Мин. срок (дней)")
    is_marked: bool = Field(False, title="Маркированный")
    is_serial_tracked: bool = Field(False, title="Серийный учёт")
    is_batch_tracked: bool = Field(False, title="Партионный учёт")
    is_expiration_tracked: bool = Field(False, title="Сроки годности")
    temperature_requirements: str = Field("", title="Темп. режим")


class ProductCreate(BaseModel):
    depositor_id: int = Field(
        ...,
        title="Поклажедатель",
        json_schema_extra={"ui_type": "select", "endpoint": "/api/v1/depositors"},
    )
    external_id: str = Field(..., title="Внешний код", min_length=1, max_length=255)
    name: str = Field(..., title="Наименование", min_length=1, max_length=255)
    sku: str = Field("", title="Артикул")
    legal_name: str = Field("", title="Полное наименование")
    weight: Decimal = Field(Decimal("0"), title="Вес нетто")
    volume: Decimal = Field(Decimal("0"), title="Объём")
    price: Decimal | None = Field(None, title="Цена")
    shelf_life_days: int | None = Field(None, title="Срок годности (дней)")
    min_shelf_life_days: int | None = Field(None, title="Мин. срок (дней)")
    is_marked: bool = Field(False, title="Маркированный")
    is_serial_tracked: bool = Field(False, title="Серийный учёт")
    is_batch_tracked: bool = Field(False, title="Партионный учёт")
    is_expiration_tracked: bool = Field(False, title="Сроки годности")
    temperature_requirements: str = Field("", title="Темп. режим")


class ProductGroupCreate(BaseModel):
    name: str = Field(..., title="Название")


class PackageCreate(BaseModel):
    product_id: int = Field(
        ...,
        title="Товар",
        json_schema_extra={"ui_type": "select", "endpoint": "/api/v1/warehouse/products"},
    )
    name: str = Field(..., title="Название")
    quantity: int = Field(1, title="Количество в упаковке")
    barcode: str | None = Field(None, title="Штрихкод")
    weight: float | None = Field(None, title="Вес брутто")
    width: float | None = Field(None, title="Ширина")
    height: float | None = Field(None, title="Высота")
    depth: float | None = Field(None, title="Глубина")
    is_base_unit: bool = Field(False, title="Базовая единица")


class ProductLocationCreate(BaseModel):
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
