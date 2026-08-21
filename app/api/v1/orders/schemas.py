"""Схемы для заказов."""

from __future__ import annotations

from datetime import date
from decimal import Decimal

from pydantic import BaseModel, Field

from app.api.v1.base_schemas import BaseRead
from app.core.statuses import OrderStatus, DeliveryStatus


class InboundOrderRead(BaseRead):
    depositor_id: int
    warehouse_id: int | None = None
    number: str
    supplier_code: str = ""
    order_date: date
    planned_date: date | None = None
    notes: str = ""
    status: str = OrderStatus.NEW.value
    pordrsp_exported: bool = False
    recadv_exported: bool = False
    has_shortage: bool = False


class InboundOrderCreate(BaseModel):
    depositor_id: int
    warehouse_id: int | None = None
    number: str = Field(min_length=1, max_length=100)
    supplier_code: str = ""
    order_date: date
    planned_date: date | None = None
    notes: str = ""


class InboundOrderUpdate(BaseModel):
    warehouse_id: int | None = None
    supplier_code: str | None = None
    planned_date: date | None = None
    notes: str | None = None
    status: str | None = None


class InboundOrderLineRead(BaseRead):
    order_id: int
    product_id: int | None = None
    quantity: Decimal
    batch_number: str = ""
    manufacture_date: date | None = None
    serial_numbers: list = Field(default_factory=list)


class InboundOrderLineCreate(BaseModel):
    order_id: int
    product_id: int | None = None
    quantity: Decimal
    batch_number: str = ""
    manufacture_date: date | None = None
    serial_numbers: list = Field(default_factory=list)


class OutboundOrderRead(BaseRead):
    depositor_id: int
    warehouse_id: int | None = None
    number: str
    customer_code: str = ""
    customer_name: str = ""
    delivery_address_name: str = ""
    order_date: date
    shipping_date: date | None = None
    needs_delivery: bool = False
    delivery_only: bool = False
    places_count: int | None = None
    declared_weight: Decimal | None = None
    delivery_contact: str = ""
    notes: str = ""
    status: str = OrderStatus.NEW.value
    ordrsp_exported: bool = False
    desadv_exported: bool = False
    zone_id: int | None = None
    document_number: str = ""
    is_printed: bool = False
    uuid: str = ""
    delivery_status: str | None = None


class OutboundOrderCreate(BaseModel):
    depositor_id: int
    warehouse_id: int | None = None
    number: str = Field(min_length=1, max_length=100)
    customer_code: str = ""
    customer_name: str = ""
    delivery_address_name: str = ""
    order_date: date
    shipping_date: date | None = None
    needs_delivery: bool = False
    delivery_only: bool = False
    places_count: int | None = None
    declared_weight: Decimal | None = None
    delivery_contact: str = ""
    notes: str = ""


class OutboundOrderUpdate(BaseModel):
    warehouse_id: int | None = None
    customer_name: str | None = None
    delivery_address_name: str | None = None
    shipping_date: date | None = None
    needs_delivery: bool | None = None
    delivery_contact: str | None = None
    notes: str | None = None
    status: str | None = None
    delivery_status: str | None = None


class OutboundOrderLineRead(BaseRead):
    order_id: int
    product_id: int | None = None
    quantity: Decimal
    location_id: int | None = None
    batch_number: str = ""
    manufacture_date: date | None = None
    serial_numbers: list = Field(default_factory=list)


class OutboundOrderLineCreate(BaseModel):
    order_id: int
    product_id: int | None = None
    quantity: Decimal
    location_id: int | None = None
    batch_number: str = ""
    manufacture_date: date | None = None
    serial_numbers: list = Field(default_factory=list)


class ReturnOrderRead(BaseRead):
    outbound_order_id: int
    inbound_order_id: int | None = None
    depositor_id: int
    warehouse_id: int | None = None
    customer_code: str = ""
    customer_name: str = ""
    return_date: date
    return_type: str = "partial"
    status: str = "new"
    notes: str = ""


class ReturnOrderCreate(BaseModel):
    outbound_order_id: int
    inbound_order_id: int | None = None
    depositor_id: int
    warehouse_id: int | None = None
    customer_code: str = ""
    customer_name: str = ""
    return_date: date
    return_type: str = "partial"
    notes: str = ""


class ReturnOrderUpdate(BaseModel):
    inbound_order_id: int | None = None
    status: str | None = None
    notes: str | None = None


class ReturnOrderLineRead(BaseRead):
    return_order_id: int
    outbound_order_line_id: int | None = None
    product_id: int
    qty_returned: Decimal
    batch_number: str = ""
    manufacture_date: date | None = None
    reason: str = ""


class ReturnOrderLineCreate(BaseModel):
    return_order_id: int
    outbound_order_line_id: int | None = None
    product_id: int
    qty_returned: Decimal
    batch_number: str = ""
    manufacture_date: date | None = None
    reason: str = ""
