"""Сервис ролей."""

from __future__ import annotations

from app.accounts.models import Role
from app.accounts.repository import RoleRepository


class RoleService:
    def __init__(self, repo: RoleRepository) -> None:
        self._repo = repo

    async def create(self, name: str, code: str, permissions: dict | None = None) -> Role:
        existing = await self._repo.get_by_code(code)
        if existing:
            raise ValueError(f"Роль с кодом {code} уже существует")

        return await self._repo.create(
            name=name,
            code=code,
            permissions=permissions or {},
        )

    async def get_by_id(self, role_id: int) -> Role | None:
        return await self._repo.get_by_id(role_id)

    async def list_all(self) -> list[Role]:
        return await self._repo.list_all()

    async def update_permissions(self, role_id: int, permissions: dict) -> Role | None:
        return await self._repo.update(role_id, permissions=permissions)

    async def has_permission(self, role: Role, permission_code: str) -> bool:
        return permission_code in role.permissions
