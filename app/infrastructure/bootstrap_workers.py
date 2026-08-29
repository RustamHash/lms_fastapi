"""Регистрация подписчиков для процессов без main.py (Celery worker)."""

from __future__ import annotations

import logging

logger = logging.getLogger(__name__)

_bootstrapped = False


def bootstrap_background_subscribers() -> None:
    """Delivery + export + notifications. Идемпотентно."""
    global _bootstrapped
    if _bootstrapped:
        return
    from app.delivery.subscribers import setup_delivery_subscribers
    from app.integration.subscribers import setup_export_subscribers
    from app.notifications.services.dispatcher import setup_notification_dispatcher

    setup_delivery_subscribers()
    setup_export_subscribers()
    setup_notification_dispatcher()
    _bootstrapped = True
    logger.info("Фоновые подписчики зарегистрированы (delivery, export, notifications)")
