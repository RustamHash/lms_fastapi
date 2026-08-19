"""Схемы для модуля delivery."""

from __future__ import annotations

from datetime import date, time

from pydantic import BaseModel, ConfigDict, Field


class DeliveryOrderRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    number: str
    contract_id: int
    document_id: int | None = None
    trade_point_id: int
    contact_person: str = ""
    phone: str = ""
    delivery_date: date | None = None
    time_from: time | None = None
    time_to: time | None = None
    status: str = "created"
    is_edo: bool = False
    comment: str = ""


class DeliveryOrderCreate(BaseModel):
    number: str
    contract_id: int
    trade_point_id: int
    document_id: int | None = None
    contact_person: str = ""
    phone: str = ""
    delivery_date: date | None = None
    time_from: time | None = None
    time_to: time | None = None
    is_edo: bool = False
    comment: str = ""


class DeliveryOrderStatusUpdate(BaseModel):
    status: str


class DriverRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    phone: str = ""
    carrier_id: int | None = None


class DriverCreate(BaseModel):
    name: str
    phone: str = ""
    carrier_id: int | None = None


class VehicleRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
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


class RouteRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
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
