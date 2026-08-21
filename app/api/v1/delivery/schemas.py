"""Схемы для модуля delivery."""

from __future__ import annotations

from datetime import date, time

from pydantic import BaseModel

from app.api.v1.base_schemas import BaseRead
from app.core.statuses import DeliveryStatus


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
