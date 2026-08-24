"""Сервис ролей."""

from __future__ import annotations

from app.accounts.models import Role
from app.accounts.repository import RoleRepository


class RoleService:
    def __init__(self, repo: RoleRepository) -> None:
        self._repo = repo

    async def get_by_id(self, role_id: int) -> Role | None:
        return await self._repo.get_by_id(role_id)

    async def list_all(self) -> list[Role]:
        return await self._repo.list_all()

    async def create(self, name: str, code: str, permissions: dict | None = None) -> Role:
        existing = await self._repo.get_by_code(code)
        if existing:
            raise ValueError(f"Роль с кодом {code} уже существует")
        return await self._repo.create(name=name, code=code, permissions=permissions or {})

    async def update(self, role_id: int, **kwargs) -> Role | None:
        return await self._repo.update(role_id, **kwargs)

    async def soft_delete(self, role_id: int, user_id: int | None = None) -> bool:
        return await self._repo.soft_delete(role_id, user_id)
