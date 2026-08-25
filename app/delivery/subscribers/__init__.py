"""Подписчики delivery на события."""

from app.delivery.subscribers.outbound_handlers import (
    handle_outbound_needs_delivery,
    setup_delivery_subscribers,
)

__all__ = ["handle_outbound_needs_delivery", "setup_delivery_subscribers"]
