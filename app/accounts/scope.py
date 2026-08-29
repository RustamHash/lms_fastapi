"""Скоуп данных пользователя: поклажедатели и клиенты.

Оператор склада (is_portal_user=False) — все поклажедатели, режут только роли.
Пользователь портала (is_portal_user=True) — только свои depositor_ids;
без привязки → пустой scope (ничего не видно), не «открой всё».
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from sqlalchemy import Select, false

if TYPE_CHECKING:
    from app.accounts.models.user import User


@dataclass(frozen=True)
class DataScope:
    unrestricted: bool
    depositor_ids: frozenset[int]
    client_ids: frozenset[int] | None
    is_portal_user: bool = False

    def allows_depositor(self, depositor_id: int) -> bool:
        if self.unrestricted:
            return True
        return depositor_id in self.depositor_ids

    def allows_client(self, client_id: int, depositor_id: int) -> bool:
        if not self.allows_depositor(depositor_id):
            return False
        if self.client_ids is None:
            return True
        return client_id in self.client_ids

    def filter_depositor(self, stmt: Select, column) -> Select:
        if self.unrestricted:
            return stmt
        if not self.depositor_ids:
            return stmt.where(false())
        return stmt.where(column.in_(self.depositor_ids))

    def filter_client(self, stmt: Select, client_column, depositor_column) -> Select:
        stmt = self.filter_depositor(stmt, depositor_column)
        if self.unrestricted or self.client_ids is None:
            return stmt
        if not self.client_ids:
            return stmt.where(false())
        return stmt.where(client_column.in_(self.client_ids))

    @property
    def single_depositor_id(self) -> int | None:
        """Единственный депозитор портала, если ровно один."""
        if self.unrestricted or len(self.depositor_ids) != 1:
            return None
        return next(iter(self.depositor_ids))


def build_scope(user: "User") -> DataScope:
    """Построить рамку видимости.

    Оператор / суперпользователь → unrestricted (роли отдельно).
    Portal-user → только привязанные депозиторы; без привязок — пустой набор.
    """
    depositor_ids = frozenset(user.depositor_ids)
    client_ids = frozenset(user.client_ids)
    is_portal = bool(getattr(user, "is_portal_user", False))

    if user.is_superuser or not is_portal:
        return DataScope(
            unrestricted=True,
            depositor_ids=frozenset(),
            client_ids=None,
            is_portal_user=False,
        )

    return DataScope(
        unrestricted=False,
        depositor_ids=depositor_ids,
        client_ids=client_ids if client_ids else None,
        is_portal_user=True,
    )
