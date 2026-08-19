"""Адаптеры интеграций."""

from app.integration.adapters.base import BaseAdapter
from app.integration.adapters.zln_adapter import ZLNAdapter

__all__ = ["BaseAdapter", "ZLNAdapter"]
