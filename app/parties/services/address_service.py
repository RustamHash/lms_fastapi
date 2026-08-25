# app/parties/services/address_service.py

"""Сервис адресов."""

from __future__ import annotations

import hashlib

from app.core.exceptions import BadRequestError
from app.infrastructure.external.dadata import DaDataClient, DaDataNotConfiguredError
from app.parties.models import Address, RawAddress
from app.parties.repository import AddressRepository, RawAddressRepository


def raw_text_hash(raw_text: str) -> str:
    canonical = " ".join(raw_text.strip().lower().split())
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


class AddressService:
    def __init__(
        self,
        repo: AddressRepository,
        raw_repo: RawAddressRepository,
        dadata: DaDataClient | None = None,
    ) -> None:
        self._repo = repo
        self._raw = raw_repo
        self._dadata = dadata or DaDataClient()

    async def get_by_id(self, id: int) -> Address | None:
        return await self._repo.get_by_id(id)

    async def list_all(self) -> list[Address]:
        return await self._repo.list_all()

    async def create(self, **kwargs) -> Address:
        return await self._repo.create(**kwargs)

    async def update(self, id: int, **kwargs) -> Address | None:
        return await self._repo.update(id, **kwargs)

    async def soft_delete(self, id: int, user_id: int | None = None) -> bool:
        return await self._repo.soft_delete(id, user_id)

    async def get_or_create(
        self,
        raw_text: str,
        source: str = "",
        user_id: int | None = None,  # created_by берётся из ContextVar
    ) -> Address:
        """Нормализовать сырой адрес через DaData и вернуть канонический Address."""
        alias = await self.resolve_alias(raw_text, source=source)
        return alias.normalized_address

    async def resolve_alias(self, raw_text: str, source: str = "") -> RawAddress:
        text = raw_text.strip()
        if not text:
            raise BadRequestError("Пустой адрес")

        digest = raw_text_hash(text)
        existing = await self._raw.get_by_hash(digest)
        if existing is not None:
            return existing

        try:
            cleaned = await self._dadata.clean_address(text)
        except DaDataNotConfiguredError as e:
            raise BadRequestError(str(e)) from e
        except ValueError as e:
            raise BadRequestError(str(e)) from e

        address = await self._find_or_create_address(cleaned)
        alias = await self._raw.create(
            raw_text=text,
            hash=digest,
            normalized_address_id=address.id,
            source=source,
        )
        await self._raw._s.refresh(alias, attribute_names=["normalized_address"])
        return alias

    async def _find_or_create_address(self, cleaned: dict) -> Address:
        fias_id = cleaned.get("fias_id") or ""
        if fias_id:
            found = await self._repo.get_by_fias_id(fias_id)
            if found is not None:
                return found

        found = await self._repo.get_by_full_address(cleaned["full_address"])
        if found is not None:
            return found

        return await self._repo.create(**cleaned)
