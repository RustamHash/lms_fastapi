"""Схемы для исходящих заказов."""

from __future__ import annotations

from datetime import date
from decimal import Decimal

from pydantic import BaseModel, Field

from app.api.v1.base_schemas import BaseRead
from app.core.statuses import OrderStatus


class OutboundOrderRead(BaseRead):
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
    number: str = Field(..., title="Номер заявки")
    customer_code: str = Field("", title="Код клиента")
    customer_name: str = Field("", title="Наименование клиента")
    client_id: int = Field(
        ...,
        title="Клиент",
        json_schema_extra={"ui_type": "select", "endpoint": "/api/v1/clients"},
    )
    delivery_address_name: str = Field("", title="Адрес доставки")
    order_date: date = Field(..., title="Дата заявки")
    shipping_date: date | None = Field(None, title="Планируемая дата отгрузки")
    needs_delivery: bool = Field(False, title="Нужна доставка")
    delivery_only: bool = Field(False, title="Только доставка")
    places_count: int | None = Field(None, title="Количество мест")
    declared_weight: Decimal | None = Field(None, title="Заявленный вес, кг")
    delivery_contact: str = Field("", title="Контакт для доставки")
    notes: str = Field("", title="Примечания")
    status: str = Field(OrderStatus.NEW.value, title="Статус")
    ordrsp_exported: bool = Field(False, title="Отклик ordrsp выгружен")
    desadv_exported: bool = Field(False, title="Уведомление desadv выгружено")
    zone_id: int | None = Field(
        None,
        title="Зона доставки",
        json_schema_extra={"ui_type": "select", "endpoint": "/api/v1/delivery-zones"},
    )
    document_number: str = Field("", title="Номер документа")
    is_printed: bool = Field(False, title="Документы распечатаны")
    uuid: str = Field("", title="UUID для QR")
    delivery_status: str | None = Field(None, title="Статус доставки")
    is_edo: bool = Field(False, title="Признак ЭДО")
    address_comment: str = Field("", title="Комментарий к адресу")
    shipping_contact: str = Field("", title="Контакт для доставки")
    total_quantity: int = Field(0, title="Общее количество штук")


class OutboundOrderCreate(BaseModel):
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
    client_id: int = Field(
        ...,
        title="Клиент",
        json_schema_extra={"ui_type": "select", "endpoint": "/api/v1/clients"},
    )
    delivery_address_name: str = Field("", title="Адрес доставки")
    order_date: date = Field(..., title="Дата заявки")
    shipping_date: date | None = Field(None, title="Планируемая дата отгрузки")
    needs_delivery: bool = Field(False, title="Нужна доставка")
    delivery_only: bool = Field(False, title="Только доставка")
    places_count: int | None = Field(None, title="Количество мест")
    declared_weight: Decimal | None = Field(None, title="Заявленный вес, кг")
    delivery_contact: str = Field("", title="Контакт для доставки")
    notes: str = Field("", title="Примечания")


class OutboundOrderUpdate(BaseModel):
    warehouse_id: int | None = Field(None, title="Склад")
    client_id: int | None = Field(
        None,
        title="Клиент",
        json_schema_extra={"ui_type": "select", "endpoint": "/api/v1/clients"},
    )
    delivery_address_name: str | None = Field(None, title="Адрес доставки")
    shipping_date: date | None = Field(None, title="Планируемая дата отгрузки")
    needs_delivery: bool | None = Field(None, title="Нужна доставка")
    delivery_contact: str | None = Field(None, title="Контакт для доставки")
    notes: str | None = Field(None, title="Примечания")
    status: str | None = Field(None, title="Статус")
    delivery_status: str | None = Field(None, title="Статус доставки")


class OutboundOrderLineRead(BaseRead):
    order_id: int = Field(..., title="Заявка")
    product_id: int | None = Field(None, title="Товар")
    quantity: Decimal = Field(..., title="Количество")
    location_id: int | None = Field(None, title="Ячейка")
    batch_number: str = Field("", title="Номер партии")
    manufacture_date: date | None = Field(None, title="Дата изготовления")
    serial_numbers: list = Field(default_factory=list, title="Серийные номера")


class OutboundOrderLineCreate(BaseModel):
    order_id: int = Field(..., title="Заявка")
    product_id: int | None = Field(
        None,
        title="Товар",
        json_schema_extra={"ui_type": "select", "endpoint": "/api/v1/warehouse/products"},
    )
    quantity: Decimal = Field(..., title="Количество")
    location_id: int | None = Field(
        None,
        title="Ячейка",
        json_schema_extra={"ui_type": "select", "endpoint": "/api/v1/warehouse/topology/locations"},
    )
    batch_number: str = Field("", title="Номер партии")
    manufacture_date: date | None = Field(None, title="Дата изготовления")
    serial_numbers: list = Field(default_factory=list, title="Серийные номера")
