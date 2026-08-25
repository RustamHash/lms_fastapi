"""Схемы для входящих заказов."""

from __future__ import annotations

from datetime import date
from decimal import Decimal

from pydantic import BaseModel, Field

from app.api.v1.base_schemas import BaseRead
from app.core.statuses import OrderStatus


class InboundOrderRead(BaseRead):
    depositor_id: int = Field(
        ...,
        title="Поклажедатель",
        json_schema_extra={"ui_type": "select", "endpoint": "/api/v1/depositors"},
    )
    warehouse_id: int | None = Field(
        None,
        title="Склад",
        json_schema_extra={"ui_type": "select", "endpoint": "/api/v1/warehouse/topology/warehouses"},
    )
    warehouse_name: str = Field("", title="Название склада")
    number: str = Field(..., title="Номер заявки")
    order_number: str = Field("", title="Номер заказа")
    loc_code: str = Field(..., title="Код склада (LOC)")
    supplier_code: str = Field("", title="Код поставщика")
    supplier_id: int = Field(
        ...,
        title="Поставщик",
        json_schema_extra={"ui_type": "select", "endpoint": "/api/v1/clients"},
    )
    order_date: date = Field(..., title="Дата заявки")
    planned_date: date | None = Field(None, title="Планируемая дата приёмки")
    notes: str = Field("", title="Примечания")
    status: str = Field(OrderStatus.NEW.value, title="Статус")
    pordrsp_exported: bool = Field(False, title="Отклик pordrsp выгружен")
    recadv_exported: bool = Field(False, title="Подтверждение recadv выгружено")
    has_shortage: bool = Field(False, title="Есть недогруз")


class InboundOrderCreate(BaseModel):
    depositor_id: int = Field(
        ...,
        title="Поклажедатель",
        json_schema_extra={"ui_type": "select", "endpoint": "/api/v1/depositors"},
    )
    warehouse_id: int | None = Field(
        None,
        title="Склад",
        json_schema_extra={"ui_type": "select", "endpoint": "/api/v1/warehouse/topology/warehouses"},
    )
    number: str = Field(..., title="Номер заявки", min_length=1, max_length=100)
    order_number: str = Field("", title="Номер заказа", max_length=100)
    loc_code: str = Field(..., title="Код склада (LOC)", min_length=1, max_length=50)
    supplier_id: int = Field(
        ...,
        title="Поставщик",
        json_schema_extra={"ui_type": "select", "endpoint": "/api/v1/clients"},
    )
    supplier_code: str = Field("", title="Код поставщика")
    order_date: date = Field(..., title="Дата заявки")
    planned_date: date | None = Field(None, title="Планируемая дата приёмки")
    notes: str = Field("", title="Примечания")


class InboundOrderUpdate(BaseModel):
    warehouse_id: int | None = Field(None, title="Склад")
    order_number: str | None = Field(None, title="Номер заказа")
    loc_code: str | None = Field(None, title="Код склада (LOC)", min_length=1, max_length=50)
    supplier_id: int | None = Field(
        None,
        title="Поставщик",
        json_schema_extra={"ui_type": "select", "endpoint": "/api/v1/clients"},
    )
    supplier_code: str | None = Field(None, title="Код поставщика")
    planned_date: date | None = Field(None, title="Планируемая дата приёмки")
    notes: str | None = Field(None, title="Примечания")
    status: str | None = Field(None, title="Статус")


class InboundOrderLineRead(BaseRead):
    order_id: int = Field(..., title="Заявка")
    product_id: int | None = Field(None, title="Товар")
    quantity: Decimal = Field(..., title="Количество")
    batch_number: str = Field("", title="Номер партии")
    manufacture_date: date | None = Field(None, title="Дата изготовления")
    serial_numbers: list = Field(default_factory=list, title="Серийные номера")


class InboundOrderLineCreate(BaseModel):
    order_id: int = Field(..., title="Заявка")
    product_id: int | None = Field(
        None,
        title="Товар",
        json_schema_extra={"ui_type": "select", "endpoint": "/api/v1/warehouse/products"},
    )
    quantity: Decimal = Field(..., title="Количество")
    batch_number: str = Field("", title="Номер партии")
    manufacture_date: date | None = Field(None, title="Дата изготовления")
    serial_numbers: list = Field(default_factory=list, title="Серийные номера")
