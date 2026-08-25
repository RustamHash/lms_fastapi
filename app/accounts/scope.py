"""Скоуп данных пользователя: поклажедатели и клиенты.

Пустые привязки = сотрудник склада, видит всё.
Только поклажедатели = менеджер поклажедателя.
Поклажедатели + клиенты = торговый агент.
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


def build_scope(user: "User") -> DataScope:
    depositor_ids = frozenset(user.depositor_ids)
    client_ids = frozenset(user.client_ids)
    if not depositor_ids:
        return DataScope(unrestricted=True, depositor_ids=frozenset(), client_ids=None)
    return DataScope(
        unrestricted=False,
        depositor_ids=depositor_ids,
        client_ids=client_ids if client_ids else None,
    )
