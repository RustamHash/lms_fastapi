"""Сервис пользователей."""

from __future__ import annotations

from app.accounts.models import User
from app.accounts.repository import UserRepository
from app.core.security import hash_password, verify_password


class UserService:
    def __init__(self, repo: UserRepository) -> None:
        self._repo = repo

    async def create(self, username: str, password: str, **kwargs) -> User:
        existing = await self._repo.get_by_username(username)
        if existing:
            raise ValueError("Пользователь уже существует")

        return await self._repo.create(
            username=username,
            password_hash=hash_password(password),
            **kwargs,
        )

    async def authenticate(self, username: str, password: str) -> User | None:
        user = await self._repo.get_by_username(username)
        if user is None:
            return None
        if not user.is_active:
            return None
        if not verify_password(password, user.password_hash):
            return None
        return user

    async def get_by_id(self, user_id: int) -> User | None:
        return await self._repo.get_by_id(user_id)

    async def list_all(self) -> list[User]:
        return await self._repo.list_all()

    async def update(self, user_id: int, **kwargs) -> User | None:
        if "password" in kwargs:
            kwargs["password_hash"] = hash_password(kwargs.pop("password"))
        return await self._repo.update(user_id, **kwargs)

    async def soft_delete(self, user_id: int, actor_id: int | None = None) -> bool:
        user = await self._repo.get_by_id(user_id)
        if not user:
            return False
        user.soft_delete(actor_id)
        await self._repo._s.flush()
        return True
