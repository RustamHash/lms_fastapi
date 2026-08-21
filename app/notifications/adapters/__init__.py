"""Адаптеры доставки уведомлений."""

from app.notifications.adapters.base import BaseAdapter
from app.notifications.adapters.app_adapter import AppAdapter
from app.notifications.adapters.email_adapter import EmailAdapter

__all__ = ["BaseAdapter", "AppAdapter", "EmailAdapter"]
