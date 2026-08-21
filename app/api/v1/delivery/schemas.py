"""Схемы для модуля delivery."""

from __future__ import annotations

from datetime import date, time
from typing import TYPE_CHECKING, Any

from pydantic import BaseModel

from app.api.v1.base_schemas import BaseRead
from app.core.statuses import DeliveryStatus

if TYPE_CHECKING:
    from app.api.v1.orders.schemas import OutboundOrderRead


class DeliveryOrderRead(BaseRead):
    number: str
    contract_id: int | None = None
    document_id: int | None = None
    outbound_order_id: int | None = None
    contact_person: str = ""
    phone: str = ""
    delivery_date: date | None = None
    time_from: time | None = None
    time_to: time | None = None
    status: str = DeliveryStatus.CREATED.value
    is_edo: bool = False
    comment: str = ""


class DeliveryOrderCreate(BaseModel):
    number: str
    contract_id: int | None = None
    document_id: int | None = None
    outbound_order_id: int | None = None
    contact_person: str = ""
    phone: str = ""
    delivery_date: date | None = None
    time_from: time | None = None
    time_to: time | None = None
    is_edo: bool = False
    comment: str = ""


class DeliveryOrderStatusUpdate(BaseModel):
    status: str


class DriverRead(BaseRead):
    name: str
    phone: str = ""
    carrier_id: int | None = None


class DriverCreate(BaseModel):
    name: str
    phone: str = ""
    carrier_id: int | None = None


class VehicleRead(BaseRead):
    number: str
    brand: str = ""
    model: str = ""
    capacity: float | None = None
    volume: float | None = None
    carrier_id: int | None = None


class VehicleCreate(BaseModel):
    number: str
    brand: str = ""
    model: str = ""
    capacity: float | None = None
    volume: float | None = None
    carrier_id: int | None = None


class RouteRead(BaseRead):
    number: str
    driver_id: int
    vehicle_id: int
    date: date
    status: str = "planned"


class RouteCreate(BaseModel):
    number: str
    driver_id: int
    vehicle_id: int
    date: date


# ========== ENRICHED ==========

class DeliveryOrderList(BaseRead):
    """Плоская схема для таблицы доставки."""
    number: str
    delivery_date: date | None = None
    status: str = "created"
    status_label: str = ""
    contact_person: str = ""
    phone: str = ""
    is_edo: bool = False

    # Плоские связи
    outbound_order_number: str | None = None
    customer_name: str | None = None
    delivery_address: str | None = None
    route_number: str | None = None
    driver_name: str | None = None
    driver_phone: str | None = None
    vehicle_number: str | None = None


class DeliveryOrderDetail(BaseRead):
    """Вложенная схема для детальной страницы доставки."""
    number: str
    contract_id: int | None = None
    document_id: int | None = None
    outbound_order_id: int | None = None
    contact_person: str = ""
    phone: str = ""
    delivery_date: date | None = None
    time_from: str | None = None
    time_to: str | None = None
    status: str = "created"
    is_edo: bool = False
    comment: str = ""

    # Вложенные
    outbound_order: Any | None = None
    route: Any | None = None
    driver: Any | None = None
    vehicle: Any | None = None
