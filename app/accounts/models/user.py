"""Модель пользователя."""

from __future__ import annotations

from sqlalchemy import Boolean, Index, String, text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship, validates
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.accounts.models.role import Role
    from app.accounts.models.user_client import UserClient
    from app.accounts.models.user_depositor import UserDepositor

from app.accounts.permissions import (
    get_all_permissions as _get_all_permissions,
)
from app.accounts.permissions import (
    has_group_access as _has_group_access,
)
from app.accounts.permissions import (
    has_permission as _has_permission,
)
from app.infrastructure.orm_base import Base


class User(Base):
    """Пользователь системы."""

    __tablename__ = "accounts_user"
    __table_args__ = (
        Index(
            "uq_accounts_user_username_alive",
            "username",
            unique=True,
            postgresql_where=text("is_deleted = false"),
        ),
        Index(
            "uq_accounts_user_email_alive",
            "email",
            unique=True,
            postgresql_where=text("email IS NOT NULL AND is_deleted = false"),
        ),
    )

    username: Mapped[str] = mapped_column(
        String(64), index=True, comment="Имя пользователя"
    )
    password_hash: Mapped[str] = mapped_column(String(255), comment="Хэш пароля")
    phone: Mapped[str] = mapped_column(String(20), default="", comment="Телефон")
    email: Mapped[str | None] = mapped_column(
        String(255), nullable=True, comment="Email"
    )
    is_superuser: Mapped[bool] = mapped_column(
        Boolean, default=False, comment="Суперпользователь"
    )
    extra_permissions: Mapped[dict[str, list[str]]] = mapped_column(
        JSONB,
        default=dict,
        comment="Дополнительные права пользователя",
    )

    roles: Mapped[list["Role"]] = relationship(
        secondary="accounts_user_roles",
        back_populates="users",
    )
    user_depositors: Mapped[list["UserDepositor"]] = relationship(
        back_populates="user",
        foreign_keys="UserDepositor.user_id",
    )
    user_clients: Mapped[list["UserClient"]] = relationship(
        back_populates="user",
        foreign_keys="UserClient.user_id",
    )

    @validates("email")
    def _normalize_email(self, _key: str, value: str | None) -> str | None:
        if value is None:
            return None
        stripped = value.strip()
        return stripped or None

    def has_permission(self, action: str, entity: str) -> bool:
        return _has_permission(self, action, entity)

    def get_all_permissions(self) -> dict[str, list[str]]:
        return _get_all_permissions(self)

    def has_group_access(self, entity: str) -> bool:
        return _has_group_access(self, entity)

    @property
    def depositor_ids(self) -> list[int]:
        """ID поклажедателей пользователя (без удалённых связей).

        Пустой список = доступ ко всем поклажедателям (оператор склада,
        логист, суперпользователь). Непустой = сотрудник поклажедателя:
        видит только своих.
        """
        return [
            row.depositor_id
            for row in self.user_depositors
            if not row.is_deleted
        ]

    @property
    def client_ids(self) -> list[int]:
        """ID клиентов пользователя (без удалённых связей).

        Пустой список при непустых depositor_ids = менеджер поклажедателя
        (все клиенты своих поклажедателей). Непустой = торговый агент.
        """
        return [
            row.client_id
            for row in self.user_clients
            if not row.is_deleted
        ]
