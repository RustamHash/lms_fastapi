"""Схемы для заказов на доставку."""

from __future__ import annotations

from datetime import date, time

from pydantic import BaseModel, Field

from app.api.v1.base_schemas import BaseRead
from app.core.statuses import DeliveryStatus


class DeliveryOrderRead(BaseRead):
    number: str = Field(..., title="Номер")
    contract_id: int | None = Field(
        None,
        title="Договор перевозки",
        json_schema_extra={"ui_type": "select", "endpoint": "/api/v1/contracts"},
    )
    document_id: int | None = Field(
        None,
        title="Документ склада",
        json_schema_extra={"ui_type": "select", "endpoint": "/api/v1/documents"},
    )
    outbound_order_id: int | None = Field(
        None,
        title="Исходящий заказ",
        json_schema_extra={"ui_type": "select", "endpoint": "/api/v1/outbound-orders"},
    )
    contact_person: str = Field("", title="Контактное лицо")
    phone: str = Field("", title="Телефон")
    delivery_date: date | None = Field(None, title="Дата доставки")
    time_from: time | None = Field(None, title="Время с")
    time_to: time | None = Field(None, title="Время до")
    status: str = Field(DeliveryStatus.CREATED.value, title="Статус")
    is_edo: bool = Field(False, title="Признак ЭДО")
    comment: str = Field("", title="Комментарий")


class DeliveryOrderCreate(BaseModel):
    number: str = Field(..., title="Номер")
    contract_id: int | None = Field(
        None,
        title="Договор перевозки",
        json_schema_extra={"ui_type": "select", "endpoint": "/api/v1/contracts"},
    )
    document_id: int | None = Field(
        None,
        title="Документ склада",
        json_schema_extra={"ui_type": "select", "endpoint": "/api/v1/documents"},
    )
    outbound_order_id: int | None = Field(
        None,
        title="Исходящий заказ",
        json_schema_extra={"ui_type": "select", "endpoint": "/api/v1/outbound-orders"},
    )
    contact_person: str = Field("", title="Контактное лицо")
    phone: str = Field("", title="Телефон")
    delivery_date: date | None = Field(None, title="Дата доставки")
    time_from: time | None = Field(None, title="Время с")
    time_to: time | None = Field(None, title="Время до")
    is_edo: bool = Field(False, title="Признак ЭДО")
    comment: str = Field("", title="Комментарий")
