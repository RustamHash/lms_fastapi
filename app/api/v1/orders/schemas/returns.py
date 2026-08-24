"""Схемы для возвратов."""

from __future__ import annotations

from datetime import date
from decimal import Decimal

from pydantic import BaseModel, Field

from app.api.v1.base_schemas import BaseRead


class ReturnOrderRead(BaseRead):
    outbound_order_id: int = Field(
        ...,
        title="Исходный исходящий заказ",
        json_schema_extra={"ui_type": "select", "endpoint": "/api/v1/outbound-orders"},
    )
    inbound_order_id: int | None = Field(
        None,
        title="Созданный приходный заказ",
        json_schema_extra={"ui_type": "select", "endpoint": "/api/v1/inbound-orders"},
    )
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
    customer_code: str = Field("", title="Код клиента")
    customer_name: str = Field("", title="Наименование клиента")
    return_date: date = Field(..., title="Дата возврата")
    return_type: str = Field("partial", title="Тип возврата")
    status: str = Field("new", title="Статус возврата")
    notes: str = Field("", title="Примечания")


class ReturnOrderCreate(BaseModel):
    outbound_order_id: int = Field(
        ...,
        title="Исходный исходящий заказ",
        json_schema_extra={"ui_type": "select", "endpoint": "/api/v1/outbound-orders"},
    )
    inbound_order_id: int | None = Field(None, title="Созданный приходный заказ")
    depositor_id: int = Field(
        ...,
        title="Поклажедатель",
        json_schema_extra={"ui_type": "select", "endpoint": "/api/v1/depositors"},
    )
    warehouse_id: int | None = Field(None, title="Склад")
    customer_code: str = Field("", title="Код клиента")
    customer_name: str = Field("", title="Наименование клиента")
    return_date: date = Field(..., title="Дата возврата")
    return_type: str = Field("partial", title="Тип возврата")
    notes: str = Field("", title="Примечания")


class ReturnOrderUpdate(BaseModel):
    inbound_order_id: int | None = Field(None, title="Созданный приходный заказ")
    status: str | None = Field(None, title="Статус возврата")
    notes: str | None = Field(None, title="Примечания")


class ReturnOrderLineRead(BaseRead):
    return_order_id: int = Field(..., title="Возврат")
    outbound_order_line_id: int | None = Field(None, title="Исходная строка")
    product_id: int = Field(..., title="Товар")
    qty_returned: Decimal = Field(..., title="Количество возвращаемого товара")
    batch_number: str = Field("", title="Партия")
    manufacture_date: date | None = Field(None, title="Дата производства")
    reason: str = Field("", title="Причина возврата")


class ReturnOrderLineCreate(BaseModel):
    return_order_id: int = Field(..., title="Возврат")
    outbound_order_line_id: int | None = Field(None, title="Исходная строка")
    product_id: int = Field(
        ...,
        title="Товар",
        json_schema_extra={"ui_type": "select", "endpoint": "/api/v1/warehouse/products"},
    )
    qty_returned: Decimal = Field(..., title="Количество возвращаемого товара")
    batch_number: str = Field("", title="Партия")
    manufacture_date: date | None = Field(None, title="Дата производства")
    reason: str = Field("", title="Причина возврата")
