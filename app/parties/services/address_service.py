"""Сервис адресов."""

from __future__ import annotations

import hashlib

import logging

from app.infrastructure.external.dadata import DaDataClient

logger = logging.getLogger(__name__)
from app.parties.models import Address
from app.parties.repository import AddressRepository


class AddressService:
    def __init__(self, repo: AddressRepository) -> None:
        self._repo = repo
        self._dadata = DaDataClient()

    @staticmethod
    def _normalize_text(text: str) -> str:
        return " ".join(text.lower().strip().split())

    @staticmethod
    def get_hash(text: str) -> str:
        normalized = AddressService._normalize_text(text)
        return hashlib.sha256(normalized.encode()).hexdigest()

    async def get_or_create(
        self, raw_text: str, source: str = "", user_id: int | None = None
    ) -> Address:
        logger.info("Разрешение адреса: %s", raw_text)
        # 1. Ищем сырой адрес по точному тексту
        raw = await self._repo.find_raw_by_text(raw_text)
        if raw:
            address = await self._repo.get_address_by_id(raw.normalized_address_id)
            if address:
                return address

        # 2. Ищем по hash
        address_hash = self.get_hash(raw_text)
        address = await self._repo.get_by_hash(address_hash)
        if address:
            # Сохраняем новый вариант сырого адреса
            await self._repo.insert_raw(
                raw_text=raw_text,
                hash=address_hash,
                normalized_address_id=address.id,
                source=source,
                created_by_id=user_id,
                updated_by_id=user_id,
            )
            return address

        # 3. DaData
        normalized_data = self._dadata.clean_address(raw_text)

        if normalized_data:
            full_address = normalized_data.get("full_address", raw_text)
            fias_id = normalized_data.get("fias_id", "")
            latitude = normalized_data.get("latitude")
            longitude = normalized_data.get("longitude")
            postal_code = normalized_data.get("postal_code", "")
            region = normalized_data.get("region", "")
            city = normalized_data.get("city", "")
            street = normalized_data.get("street", "")
            house = normalized_data.get("house", "")
        else:
            full_address = raw_text
            fias_id = ""
            latitude = None
            longitude = None
            postal_code = ""
            region, city, street, house = self._parse_raw_address(raw_text)

        # 3a. Парсим компоненты из DaData если есть
        if not region and normalized_data:
            region = normalized_data.get("region", "")
            city = normalized_data.get("city", "")
            street = normalized_data.get("street", "")
            house = normalized_data.get("house", "")

        # 4. Ищем канонический по fias_id
        if fias_id:
            address = await self._repo.find_address_by_fias_id(fias_id)
            if address:
                await self._repo.insert_raw(
                    raw_text=raw_text,
                    hash=address_hash,
                    normalized_address_id=address.id,
                    source=source,
                    created_by_id=user_id,
                    updated_by_id=user_id,
                )
                return address

        # 5. Ищем канонический по full_address
        address = await self._repo.find_address_by_full_address(full_address)
        if address:
            await self._repo.insert_raw(
                raw_text=raw_text,
                hash=address_hash,
                normalized_address_id=address.id,
                source=source,
                created_by_id=user_id,
                updated_by_id=user_id,
            )
            return address

        # 6. Создаём канонический адрес
        logger.info("Создание нового адреса: %s", full_address)
        address = await self._repo.insert_address(
            full_address=full_address,
            region=region,
            city=city,
            street=street,
            house=house,
            fias_id=fias_id,
            latitude=latitude,
            longitude=longitude,
            postal_code=postal_code,
            delivery_zone_id=None,
            created_by_id=user_id,
            updated_by_id=user_id,
        )

        # 7. Создаём сырой адрес с привязкой
        await self._repo.insert_raw(
            raw_text=raw_text,
            hash=address_hash,
            normalized_address_id=address.id,
            source=source,
            created_by_id=user_id,
            updated_by_id=user_id,
        )

        return address

    @staticmethod
    def _parse_raw_address(raw: str) -> tuple[str, str, str, str]:
        """Грубый разбор строки по запятым: (region, city, street, house)."""
        parts = [p.strip() for p in raw.split(",") if p.strip()]
        if not parts:
            return ("", "", "", "")
        
        region = parts[0] if len(parts) > 0 else ""
        city = parts[1] if len(parts) > 1 else ""
        street = parts[2] if len(parts) > 2 else ""
        house = parts[3] if len(parts) > 3 else ""
        return (region, city, street, house)

    async def get_by_id(self, address_id: int) -> Address | None:
        return await self._repo.get_address_by_id(address_id)

    async def list_all(self) -> list[Address]:
        return await self._repo.list_addresses()

    async def soft_delete(self, address_id: int, user_id: int | None = None) -> bool:
        address = await self._repo.get_address_by_id(address_id)
        if not address:
            return False
        address.soft_delete(user_id)
        await self._repo.session.flush()
        return True
