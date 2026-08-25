"""Клиент DaData для нормализации адресов."""

from __future__ import annotations

import asyncio
import logging
from decimal import Decimal, InvalidOperation
from typing import Any

from app.core.config import get_settings

logger = logging.getLogger(__name__)


class DaDataNotConfiguredError(RuntimeError):
    """Нет DADATA_TOKEN / DADATA_SECRET."""


class DaDataClient:
    """Обёртка над API DaData. Синхронный SDK вызывается в потоке."""

    def __init__(self) -> None:
        settings = get_settings()
        self.token = settings.dadata_token
        self.secret = settings.dadata_secret
        self._client = None

    def _init_client(self):
        if self._client is None:
            from dadata import Dadata

            self._client = Dadata(self.token, self.secret)
        return self._client

    async def clean_address(self, raw_address: str) -> dict[str, Any]:
        """Нормализация адреса. Пустой результат — ошибка, не None."""
        if not self.token or not self.secret:
            raise DaDataNotConfiguredError(
                "DaData не настроен (DADATA_TOKEN / DADATA_SECRET)"
            )
        return await asyncio.to_thread(self._clean_sync, raw_address)

    def _clean_sync(self, raw_address: str) -> dict[str, Any]:
        client = self._init_client()
        result = client.clean("address", raw_address)

        if isinstance(result, list):
            result = result[0] if result else {}

        if not result:
            raise ValueError(f"DaData не вернул адрес: {raw_address}")

        full = (result.get("result") or "").strip()
        if not full:
            raise ValueError(f"DaData не смог разобрать адрес: {raw_address}")

        block = (result.get("block") or "").strip()
        block_type = (result.get("block_type") or "").lower()
        building = ""
        structure = ""
        if block_type in {"стр", "строение", "соор", "сооружение"}:
            structure = block
        else:
            building = block

        logger.info("DaData clean: %s -> %s", raw_address, full)

        return {
            "full_address": full,
            "fias_id": result.get("fias_id") or "",
            "latitude": _coord(result.get("geo_lat")),
            "longitude": _coord(result.get("geo_lon")),
            "postal_code": result.get("postal_code") or "",
            "region": result.get("region_with_type") or "",
            "city": result.get("city_with_type")
            or result.get("settlement_with_type")
            or "",
            "street": result.get("street_with_type") or "",
            "house": result.get("house") or "",
            "building": building,
            "structure": structure,
            "flat": result.get("flat") or "",
        }


def _coord(value: Any) -> Decimal | None:
    if value is None or value == "":
        return None
    try:
        return Decimal(str(value))
    except InvalidOperation:
        return None
