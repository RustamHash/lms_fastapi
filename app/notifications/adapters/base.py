"""Базовый адаптер доставки."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class BaseAdapter(ABC):
    """Базовый класс адаптера."""

    channel: str = "base"

    @abstractmethod
    async def send(self, recipient: dict[str, Any], notification: dict[str, Any]) -> None:
        """Отправить уведомление."""
        ...
