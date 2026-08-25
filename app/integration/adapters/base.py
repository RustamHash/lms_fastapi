"""Базовый адаптер: файл партнёра → сообщение домена заказов."""

from __future__ import annotations

from abc import ABC, abstractmethod

from app.orders.exchange_messages import InboundExchangeMessage, OutboundExchangeMessage

ExchangeMessage = InboundExchangeMessage | OutboundExchangeMessage


class BaseAdapter(ABC):
    @abstractmethod
    async def parse(
        self, file_path: str
    ) -> tuple[ExchangeMessage | None, list[str]]:
        """PORDER/ORDER → сообщение домена. Ошибки — список строк, сообщение None."""
        ...
