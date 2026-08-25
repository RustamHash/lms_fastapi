"""Сервис пользователей."""

from __future__ import annotations

from sqlalchemy import select

from app.accounts.models import User
from app.accounts.repository import (
    RoleRepository,
    UserClientRepository,
    UserDepositorRepository,
    UserRepository,
)
from app.core.security import hash_password, verify_password


def _normalize_email(email: str | None) -> str | None:
    if email is None:
        return None
    stripped = email.strip()
    return stripped or None


class UserService:
    def __init__(
        self,
        repo: UserRepository,
        role_repo: RoleRepository | None = None,
        user_depositor_repo: UserDepositorRepository | None = None,
        user_client_repo: UserClientRepository | None = None,
    ) -> None:
        self._repo = repo
        self._role_repo = role_repo
        self._user_depositor_repo = user_depositor_repo
        self._user_client_repo = user_client_repo

    async def get_by_id(self, user_id: int, *, with_depositors: bool = False) -> User | None:
        return await self._repo.get_by_id(user_id, with_depositors=with_depositors)

    async def list_all(self) -> list[User]:
        return await self._repo.list_all()

    async def create(self, username: str, password: str, **kwargs) -> User:
        existing = await self._repo.get_by_username(username)
        if existing:
            raise ValueError("Пользователь уже существует")

        if "email" in kwargs:
            kwargs["email"] = _normalize_email(kwargs["email"])

        return await self._repo.create(
            username=username,
            password_hash=hash_password(password),
            **kwargs,
        )

    async def authenticate(self, username: str, password: str) -> User | None:
        user = await self._repo.get_by_username(username)
        if user is None:
            return None
        if user.is_deleted or not user.is_active:
            return None
        if not verify_password(password, user.password_hash):
            return None
        return user

    async def update(self, user_id: int, **kwargs) -> User | None:
        if "password" in kwargs:
            kwargs["password_hash"] = hash_password(kwargs.pop("password"))
        if "email" in kwargs:
            kwargs["email"] = _normalize_email(kwargs["email"])
        return await self._repo.update(user_id, **kwargs)

    async def soft_delete(self, user_id: int, actor_id: int | None = None) -> bool:
        return await self._repo.soft_delete(user_id, actor_id)

    async def set_roles(self, user_id: int, role_ids: list[int]) -> User | None:
        if self._role_repo is None:
            raise RuntimeError("RoleRepository не передан в UserService")
        user = await self._repo.get_by_id(user_id, with_depositors=True)
        if user is None:
            return None
        unique_ids = list(dict.fromkeys(role_ids))
        roles = await self._role_repo.list_by_ids(unique_ids)
        if len(roles) != len(unique_ids):
            raise ValueError("Некоторые роли не найдены")
        await self._repo.set_roles(user, roles)
        return await self._repo.get_by_id(user_id, with_depositors=True)

    async def set_depositors(self, user_id: int, depositor_ids: list[int]) -> User | None:
        if self._user_depositor_repo is None:
            raise RuntimeError("UserDepositorRepository не передан в UserService")
        user = await self._repo.get_by_id(user_id, with_depositors=True)
        if user is None:
            return None
        unique_ids = list(dict.fromkeys(depositor_ids))
        if unique_ids:
            from app.parties.models.counterparty import Depositor

            found = set(
                await self._user_depositor_repo._s.scalars(
                    select(Depositor.id).where(
                        Depositor.id.in_(unique_ids),
                        Depositor.is_deleted.is_(False),
                    )
                )
            )
            if found != set(unique_ids):
                raise ValueError("Некоторые поклажедатели не найдены")
        await self._user_depositor_repo.replace_for_user(user, unique_ids)
        user = await self._repo.get_by_id(user_id, with_depositors=True)
        if user is not None and self._user_client_repo is not None:
            await self._prune_clients(user, set(unique_ids))
            user = await self._repo.get_by_id(user_id, with_depositors=True)
        return user

    async def set_clients(self, user_id: int, client_ids: list[int]) -> User | None:
        if self._user_client_repo is None:
            raise RuntimeError("UserClientRepository не передан в UserService")
        user = await self._repo.get_by_id(user_id, with_depositors=True)
        if user is None:
            return None
        unique_ids = list(dict.fromkeys(client_ids))
        if unique_ids and not user.depositor_ids:
            raise ValueError("Сначала назначьте поклажедателей")
        if unique_ids:
            from app.parties.models.client import Client

            rows = list(
                await self._user_client_repo._s.scalars(
                    select(Client).where(
                        Client.id.in_(unique_ids),
                        Client.is_deleted.is_(False),
                    )
                )
            )
            if len(rows) != len(unique_ids):
                raise ValueError("Некоторые клиенты не найдены")
            allowed = set(user.depositor_ids)
            if any(row.depositor_id not in allowed for row in rows):
                raise ValueError("Клиент не принадлежит назначенным поклажедателям")
        await self._user_client_repo.replace_for_user(user, unique_ids)
        return await self._repo.get_by_id(user_id, with_depositors=True)

    async def _prune_clients(self, user: User, depositor_ids: set[int]) -> None:
        if self._user_client_repo is None:
            return
        keep: list[int] = []
        for row in user.user_clients:
            if row.is_deleted:
                continue
            if not depositor_ids:
                continue
            client = row.client if "client" in row.__dict__ else None
            if client is None:
                from app.parties.models.client import Client

                client = await self._user_client_repo._s.get(Client, row.client_id)
            if client is not None and client.depositor_id in depositor_ids:
                keep.append(row.client_id)
        await self._user_client_repo.replace_for_user(user, keep)
