"""Сервис юрлиц."""

from __future__ import annotations

from app.parties.models import LegalEntity
from app.parties.repository import LegalEntityRepository


class LegalEntityService:
    def __init__(self, repo: LegalEntityRepository) -> None:
        self._repo = repo

    async def create(self, user_id: int | None, **kwargs) -> LegalEntity:
        name = kwargs.get("name")
        if not name:
            raise ValueError("Наименование обязательно")

        # 0 → None для FK
        if kwargs.get("legal_address_id") == 0:
            kwargs["legal_address_id"] = None
        if kwargs.get("actual_address_id") == 0:
            kwargs["actual_address_id"] = None

        inn = kwargs.get("inn")
        if inn:
            existing = await self._repo.get_by_inn(inn)
            if existing:
                raise ValueError(f"Юрлицо с ИНН {inn} уже существует")

        return await self._repo.insert(
            **kwargs,
        )

    async def get_by_id(self, entity_id: int) -> LegalEntity | None:
        return await self._repo.get_by_id(entity_id)

    async def get_by_inn(self, inn: str) -> LegalEntity | None:
        return await self._repo.get_by_inn(inn)

    async def list_all(self) -> list[LegalEntity]:
        return await self._repo.list_all()

    async def update(self, entity_id: int, user_id: int | None, **fields) -> LegalEntity | None:
        return await self._repo.update(entity_id, **fields)

    async def soft_delete(self, entity_id: int, user_id: int | None = None) -> bool:
        entity = await self._repo.get_by_id(entity_id)
        if not entity:
            return False
        entity.soft_delete(user_id)
        await self._repo.session.flush()
        return True
