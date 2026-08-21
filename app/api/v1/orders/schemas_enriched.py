"""Обогащенные схемы для списков и детальных страниц."""

from __future__ import annotations

from datetime import date
from decimal import Decimal
from typing import TYPE_CHECKING, Any

from app.api.v1.base_schemas import BaseRead

if TYPE_CHECKING:
    from app.api.v1.parties.schemas import AddressRead, ClientRead, DeliveryZoneRead, DepositorRead
    from app.api.v1.warehouse.schemas import WarehouseRead
    from app.api.v1.delivery.schemas import DeliveryOrderRead, DriverRead, RouteRead


# ========== OUTBOUND ORDER ==========

class OutboundOrderList(BaseRead):
    """Плоская схема для таблицы."""
    number: str
    customer_code: str = ""
    customer_name: str = ""
    document_number: str = ""
    delivery_address_name: str = ""
    order_date: date
    shipping_date: date | None = None
    status: str = "new"
    status_label: str = ""
    is_edo: bool = False
    warehouse_id: int | None = None
    declared_weight: Decimal | None = None
    needs_delivery: bool = False
    notes: str = ""
    address_comment: str = ""
    shipping_contact: str = ""
    total_quantity: int = 0
    total_lines: int = 0

    # Плоские связи
    depositor_name: str | None = None
    zone_name: str | None = None
    warehouse_name: str | None = None
    route_number: str | None = None
    driver_name: str | None = None
    driver_phone: str | None = None


class OutboundOrderDetail(BaseRead):
    """Вложенная схема для детальной страницы."""
    number: str
    customer_code: str = ""
    customer_name: str = ""
    document_number: str = ""
    delivery_address_name: str = ""
    order_date: date
    shipping_date: date | None = None
    status: str = "new"
    is_edo: bool = False
    warehouse_id: int | None = None
    declared_weight: Decimal | None = None
    needs_delivery: bool = False
    delivery_only: bool = False
    places_count: int | None = None
    delivery_contact: str = ""
    notes: str = ""

    # Вложенные связи
    depositor: Any | None = None
    client: Any | None = None
    warehouse: Any | None = None
    delivery_order: Any | None = None
    route: Any | None = None
    driver: Any | None = None
    delivery_address: Any | None = None
    zone: Any | None = None
    documents: list = []
    tasks: list = []
    returns: list = []


# ========== INBOUND ORDER ==========

class InboundOrderList(BaseRead):
    """Плоская схема для таблицы приходных."""
    number: str
    supplier_code: str = ""
    order_date: date
    planned_date: date | None = None
    status: str = "new"
    status_label: str = ""
    has_shortage: bool = False
    warehouse_id: int | None = None
    notes: str = ""

    # Плоские связи
    depositor_name: str | None = None
    supplier_name: str | None = None
    warehouse_name: str | None = None


class InboundOrderDetail(BaseRead):
    """Вложенная схема для детальной страницы приходного."""
    number: str
    supplier_code: str = ""
    order_date: date
    planned_date: date | None = None
    status: str = "new"
    has_shortage: bool = False
    warehouse_id: int | None = None
    notes: str = ""

    # Вложенные
    depositor: Any | None = None
    supplier: Any | None = None
    warehouse: Any | None = None


# ========== ORDER LINES ==========

class OutboundOrderLineList(BaseRead):
    """Строка заказа для таблицы."""
    order_id: int
    product_id: int | None = None
    quantity: Decimal
    location_id: int | None = None
    batch_number: str = ""
    manufacture_date: date | None = None

    # Плоские связи
    product_name: str | None = None
    product_sku: str | None = None
    location_name: str | None = None


class InboundOrderLineList(BaseRead):
    """Строка приходного заказа для таблицы."""
    order_id: int
    product_id: int | None = None
    quantity: Decimal
    batch_number: str = ""
    manufacture_date: date | None = None

    # Плоские связи
    product_name: str | None = None
    product_sku: str | None = None
