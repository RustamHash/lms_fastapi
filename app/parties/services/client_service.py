"""Сервис клиентов и торговых точек."""

from __future__ import annotations

from app.parties.models import Client, TradePoint
from app.parties.repository import ClientRepository, TradePointRepository


class ClientService:
    def __init__(self, repo: ClientRepository) -> None:
        self._repo = repo

    async def create(self, user_id: int | None, **kwargs) -> Client:
        if not kwargs.get("depositor_id"):
            raise ValueError("Поклажедатель обязателен")
        if not kwargs.get("external_id"):
            raise ValueError("Внешний код обязателен")
        if not kwargs.get("name"):
            raise ValueError("Наименование обязательно")

        existing = await self._repo.get_by_external_id(
            kwargs["depositor_id"], kwargs["external_id"]
        )
        if existing:
            raise ValueError(f"Клиент с кодом {kwargs['external_id']} уже существует")

        return await self._repo.insert(
            created_by_id=user_id,
            updated_by_id=user_id,
            **kwargs,
        )

    async def get_or_create(self, user_id: int | None, **kwargs) -> tuple[Client, bool]:
        client = await self._repo.get_by_external_id(
            kwargs.get("depositor_id"), kwargs.get("external_id")
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
        return await self._repo.update(client_id, updated_by_id=user_id, **fields)

    async def soft_delete(self, client_id: int, user_id: int | None = None) -> bool:
        client = await self._repo.get_by_id(client_id)
        if not client:
            return False
        client.soft_delete(user_id)
        await self._repo.session.flush()
        return True


class TradePointService:
    def __init__(self, repo: TradePointRepository) -> None:
        self._repo = repo

    async def get_or_create(
        self, client_id: int, address_id: int, name: str = "", user_id: int | None = None
    ) -> tuple[TradePoint, bool]:
        tp = await self._repo.get_by_client_and_address(client_id, address_id)
        if tp:
            return tp, False
        tp = await self._repo.insert(
            client_id=client_id,
            address_id=address_id,
            name=name,
            created_by_id=user_id,
            updated_by_id=user_id,
        )
        return tp, True

    async def get_by_id(self, tp_id: int) -> TradePoint | None:
        return await self._repo.get_by_id(tp_id)

    async def list_by_client(self, client_id: int) -> list[TradePoint]:
        return await self._repo.list_by_client(client_id)
