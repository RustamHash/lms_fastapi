"""Схемы модуля delivery."""

from app.api.v1.delivery.schemas.orders import DeliveryOrderRead, DeliveryOrderCreate
from app.api.v1.delivery.schemas.drivers import DriverRead, DriverCreate
from app.api.v1.delivery.schemas.vehicles import VehicleRead, VehicleCreate
from app.api.v1.delivery.schemas.routes import (
    RouteAssignOrder,
    RouteLineRead,
    RouteRead,
    RouteCreate,
)

__all__ = [
    "DeliveryOrderRead",
    "DeliveryOrderCreate",
    "DriverRead",
    "DriverCreate",
    "VehicleRead",
    "VehicleCreate",
    "RouteRead",
    "RouteCreate",
    "RouteAssignOrder",
    "RouteLineRead",
]
