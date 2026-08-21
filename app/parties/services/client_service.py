"""Сервис клиентов и торговых точек."""

from __future__ import annotations

from app.parties.models import Client
from app.parties.repository import ClientRepository


class ClientService:
    def __init__(self, repo: ClientRepository) -> None:
        self._repo = repo

    async def create(self, user_id: int | None, **kwargs) -> Client:
        if not kwargs.get("depositor_id"):
            raise ValueError("Поклажедатель обязателен")
        if not kwargs.get("code"):
            raise ValueError("Внешний код обязателен")
        if not kwargs.get("name"):
            raise ValueError("Наименование обязательно")

        existing = await self._repo.get_by_code(
            kwargs["depositor_id"], kwargs["code"]
        )
        if existing:
            raise ValueError(f"Клиент с кодом {kwargs['code']} уже существует")

        return await self._repo.insert(
            **kwargs,
        )

    async def get_or_create(self, user_id: int | None, **kwargs) -> tuple[Client, bool]:
        client = await self._repo.get_by_code(
            kwargs.get("depositor_id"), kwargs.get("code")
        )
        if client:
            return client, False
        client = await self.create(user_id=user_id, **kwargs)
        return client, True

    async def get_by_id(self, client_id: int) -> Client | None:
        return await self._repo.get_by_id(client_id)

    async def list_by_depositor(self, depositor_id: int) -> list[Client]:
        return await self._repo.list_by_depositor(depositor_id)

    async def update(self, client_id: int, user_id: int | None, **fields) -> Client | None:
        return await self._repo.update(client_id, **fields)

    async def soft_delete(self, client_id: int, user_id: int | None = None) -> bool:
        client = await self._repo.get_by_id(client_id)
        if not client:
            return False
        client.soft_delete(user_id)
        await self._repo.session.flush()
        return True
