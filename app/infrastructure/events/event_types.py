"""Типы событий системы."""

from __future__ import annotations


class EventTypes:
    """Все типы событий."""

    IMPORT_COMPLETED = "import.completed"
    IMPORT_FAILED = "import.failed"

    DOCUMENT_CREATED = "document.created"
    DOCUMENT_STATUS_CHANGED = "document.status_changed"

    DELIVERY_ORDER_CREATED = "delivery_order.created"
    DELIVERY_ORDER_ASSIGNED = "delivery_order.assigned"
    DELIVERY_ORDER_IN_TRANSIT = "delivery_order.in_transit"
    DELIVERY_ORDER_DELIVERED = "delivery_order.delivered"
    DELIVERY_ORDER_CANCELLED = "delivery_order.cancelled"

    ROUTE_ASSIGNED = "route.assigned"

    TASK_CREATED = "task.created"
    TASK_COMPLETED = "task.completed"
