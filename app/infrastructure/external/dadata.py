"""Клиент DaData для нормализации адресов."""

from __future__ import annotations

from typing import Any

from app.core.config import get_settings


class DaDataClient:
    """Обёртка над API DaData."""

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

    def clean_address(self, raw_address: str) -> dict[str, Any] | None:
        """Нормализация адреса через DaData clean."""
        if not self.token or not self.secret:
            return None

        try:
            client = self._init_client()
            result = client.clean("address", raw_address)

            if not result:
                return None

            if isinstance(result, list):
                result = result[0] if result else {}

            return {
                "full_address": result.get("result", raw_address),
                "fias_id": result.get("fias_id", ""),
                "latitude": result.get("geo_lat"),
                "longitude": result.get("geo_lon"),
                "postal_code": result.get("postal_code", ""),
                "region": result.get("region_with_type", ""),
                "city": result.get("city_with_type") or result.get("settlement_with_type", ""),
                "street": result.get("street_with_type", ""),
                "house": result.get("house", ""),
            }
        except Exception:
            return None
