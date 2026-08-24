# app/parties/services/client_service.py

"""Сервис клиентов."""

from __future__ import annotations

from app.parties.models import Client
from app.parties.repository import ClientRepository


class ClientService:
    def __init__(self, repo: ClientRepository) -> None:
        self._repo = repo

    async def get_by_id(self, id: int) -> Client | None:
        return await self._repo.get_by_id(id)

    async def list_all(self) -> list[Client]:
        return await self._repo.list_all()

    async def create(self, **kwargs) -> Client:
        return await self._repo.create(**kwargs)

    async def update(self, id: int, **kwargs) -> Client | None:
        return await self._repo.update(id, **kwargs)

    async def soft_delete(self, id: int, user_id: int | None = None) -> bool:
        return await self._repo.soft_delete(id, user_id)
