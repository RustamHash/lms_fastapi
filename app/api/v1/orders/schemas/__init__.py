"""Схемы модуля orders."""

from app.api.v1.orders.schemas.inbound import (
    InboundOrderRead,
    InboundOrderCreate,
    InboundOrderUpdate,
    InboundOrderLineRead,
    InboundOrderLineCreate,
)
from app.api.v1.orders.schemas.outbound import (
    OutboundOrderRead,
    OutboundOrderCreate,
    OutboundOrderUpdate,
    OutboundOrderLineRead,
    OutboundOrderLineCreate,
)
from app.api.v1.orders.schemas.returns import (
    ReturnOrderRead,
    ReturnOrderCreate,
    ReturnOrderUpdate,
    ReturnOrderLineRead,
    ReturnOrderLineCreate,
)

__all__ = [
    # Inbound
    "InboundOrderRead",
    "InboundOrderCreate",
    "InboundOrderUpdate",
    "InboundOrderLineRead",
    "InboundOrderLineCreate",
    # Outbound
    "OutboundOrderRead",
    "OutboundOrderCreate",
    "OutboundOrderUpdate",
    "OutboundOrderLineRead",
    "OutboundOrderLineCreate",
    # Returns
    "ReturnOrderRead",
    "ReturnOrderCreate",
    "ReturnOrderUpdate",
    "ReturnOrderLineRead",
    "ReturnOrderLineCreate",
]
