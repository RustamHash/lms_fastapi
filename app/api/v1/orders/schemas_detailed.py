"""Детальные схемы заказов с вложенными объектами."""

from __future__ import annotations

from datetime import date
from app.api.v1.base_schemas import BaseRead
from app.api.v1.parties.schemas import DepositorRead, ClientRead
from app.api.v1.warehouse.schemas import WarehouseRead


class InboundOrderDetailed(BaseRead):
    """Приходный заказ с поставщиком и складом."""

    depositor_id: int
    warehouse_id: int | None = None
    number: str
    supplier_code: str = ""
    order_date: date
    planned_date: date | None = None
    status: str = "new"
    has_shortage: bool = False

    # Вложенные
    depositor: DepositorRead | None = None
    supplier: ClientRead | None = None
    warehouse: WarehouseRead | None = None


class OutboundOrderDetailed(BaseRead):
    """Расходный заказ с клиентом, поклажедателем, маршрутом."""

    depositor_id: int
    warehouse_id: int | None = None
    number: str
    customer_code: str = ""
    customer_name: str = ""
    delivery_address_name: str = ""
    order_date: date
    shipping_date: date | None = None
    needs_delivery: bool = False
    status: str = "new"
    delivery_status: str | None = None

    # Вложенные
    depositor: DepositorRead | None = None
    client: ClientRead | None = None
    warehouse: WarehouseRead | None = None
