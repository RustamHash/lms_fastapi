"""Сервис поклажедателей."""

from __future__ import annotations

from app.parties.models import Depositor
from app.parties.repository import DepositorRepository


class DepositorService:
    def __init__(self, repo: DepositorRepository) -> None:
        self._repo = repo

    async def create(
        self, legal_entity_id: int, code: str = "", user_id: int | None = None
    ) -> Depositor:
        if not legal_entity_id:
            raise ValueError("Юрлицо обязательно")

        if code:
            existing = await self._repo.get_by_code(code)
            if existing:
                raise ValueError(f"Поклажедатель с кодом {code} уже существует")

        return await self._repo.insert(
            legal_entity_id=legal_entity_id,
            code=code,
            created_by_id=user_id,
            updated_by_id=user_id,
        )

    async def get_by_id(self, depositor_id: int) -> Depositor | None:
        return await self._repo.get_by_id(depositor_id)

    async def get_by_code(self, code: str) -> Depositor | None:
        return await self._repo.get_by_code(code)

    async def list_all(self) -> list[Depositor]:
        return await self._repo.list_all()
