"""Базовый адаптер: файл партнёра → сообщение домена заказов."""

from __future__ import annotations

from abc import ABC, abstractmethod

from app.orders.exchange_messages import InboundExchangeMessage


class BaseAdapter(ABC):
    @abstractmethod
    async def parse(
        self, file_path: str
    ) -> tuple[InboundExchangeMessage | None, list[str]]:
        """PORDER → InboundExchangeMessage. Иной тип — ошибка списка, сообщение None."""
        ...
