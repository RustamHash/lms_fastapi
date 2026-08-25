# app/parties/services/client_service.py

"""Сервис клиентов."""

from __future__ import annotations

from app.parties.models import Client
from app.parties.repository import ClientRepository
from app.accounts.scope import DataScope


class ClientService:
    def __init__(self, repo: ClientRepository) -> None:
        self._repo = repo

    async def get_by_id(self, id: int, scope: DataScope | None = None) -> Client | None:
        return await self._repo.get_by_id(id, scope=scope)

    async def list_all(self, scope: DataScope | None = None) -> list[Client]:
        return await self._repo.list_all(scope=scope)

    async def create(self, **kwargs) -> Client:
        return await self._repo.create(**kwargs)

    async def get_or_create(
        self,
        *,
        user_id: int | None = None,  # created_by берётся из ContextVar
        depositor_id: int,
        code: str,
        name: str,
        legal_name: str = "",
        inn: str = "",
        kpp: str = "",
        delivery_address_id: int | None = None,
        is_edo: bool = False,
    ) -> tuple[Client, bool]:
        existing = await self._repo.get_by_code(
            depositor_id, code, delivery_address_id=delivery_address_id
        )
        if existing is not None:
            return existing, False

        client = await self._repo.create(
            depositor_id=depositor_id,
            code=code,
            name=name,
            legal_name=legal_name,
            inn=inn,
            kpp=kpp,
            delivery_address_id=delivery_address_id,
            is_edo=is_edo,
        )
        return client, True

    async def update(self, id: int, **kwargs) -> Client | None:
        return await self._repo.update(id, **kwargs)

    async def soft_delete(self, id: int, user_id: int | None = None) -> bool:
        return await self._repo.soft_delete(id, user_id)
