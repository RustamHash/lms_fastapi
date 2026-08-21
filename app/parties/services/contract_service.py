"""Сервис договоров."""

from __future__ import annotations

from app.parties.models import Contract
from app.parties.repository import ContractRepository


class ContractService:
    def __init__(self, repo: ContractRepository) -> None:
        self._repo = repo

    async def create(self, user_id: int | None, **kwargs) -> Contract:
        if not kwargs.get("customer_id"):
            raise ValueError("Заказчик обязателен")
        if not kwargs.get("executor_id"):
            raise ValueError("Исполнитель обязателен")
        if not kwargs.get("contract_type"):
            raise ValueError("Тип договора обязателен")
        if not kwargs.get("start_date"):
            raise ValueError("Дата начала обязательна")

        return await self._repo.insert(
            status="active",
            **kwargs,
        )

    async def get_by_id(self, contract_id: int) -> Contract | None:
        return await self._repo.get_by_id(contract_id)

    async def list_active(self) -> list[Contract]:
        return await self._repo.list_active()

    async def update(self, contract_id: int, user_id: int | None, **fields) -> Contract | None:
        return await self._repo.update(contract_id, **fields)

    async def soft_delete(self, contract_id: int, user_id: int | None = None) -> bool:
        contract = await self._repo.get_by_id(contract_id)
        if not contract:
            return False
        contract.soft_delete(user_id)
        await self._repo.session.flush()
        return True
