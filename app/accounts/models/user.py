"""Модель пользователя."""

from __future__ import annotations

from typing import Any

from sqlalchemy import Boolean, String
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.accounts.models.role import Role
from app.infrastructure.orm_base import Base


class User(Base):
    """Пользователь системы."""

    __tablename__ = "accounts_user"

    username: Mapped[str] = mapped_column(
        String(64), unique=True, index=True, comment="Имя пользователя"
    )
    password_hash: Mapped[str] = mapped_column(String(255), comment="Хэш пароля")
    phone: Mapped[str] = mapped_column(String(20), default="", comment="Телефон")
    email: Mapped[str] = mapped_column(String(255), default="", comment="Email")
    is_superuser: Mapped[bool] = mapped_column(
        Boolean, default=False, comment="Суперпользователь"
    )
    extra_permissions: Mapped[dict[str, list[str]]] = mapped_column(
        JSONB,
        default=dict,
        comment="Дополнительные права пользователя",
    )

    roles: Mapped[list["Role"]] = relationship(lazy="selectin", 
        secondary="accounts_user_roles",
        back_populates="users",
    )

    def has_permission(self, action: str, entity: str) -> bool:
        """
        Проверка права пользователя.

        Args:
            action: Действие (view, create, update, delete, approve, execute, complete)
            entity: Сущность/модуль (products, documents, delivery, users, ...)

        Returns:
            True, если право есть
        """
        # Суперпользователь имеет все права
        if self.is_superuser:
            return True

        # Проверяем личные дополнительные права
        if self._has_extra_permission(action, entity):
            return True

        # Проверяем права ролей
        for role in self.roles:
            if self._has_role_permission(role, action, entity):
                return True

        return False

    def _has_extra_permission(self, action: str, entity: str) -> bool:
        """Проверка личных прав пользователя."""
        if not self.extra_permissions:
            return False

        allowed_actions = self.extra_permissions.get(entity, [])
        return action in allowed_actions

    def _has_role_permission(self, role: "Role", action: str, entity: str) -> bool:
        """Проверка прав роли."""
        permissions = role.permissions or {}
        allowed_actions = permissions.get(entity, [])
        return action in allowed_actions

    def get_all_permissions(self) -> dict[str, list[str]]:
        """
        Возвращает все права пользователя (объединение ролей и личных).

        Returns:
            Словарь вида: {"products": ["view", "create"], ...}
        """
        if self.is_superuser:
            return {"all": ["all"]}

        result: dict[str, list[str]] = {}

        # Собираем права из ролей
        for role in self.roles:
            permissions = role.permissions or {}
            for entity, actions in permissions.items():
                if entity not in result:
                    result[entity] = []
                for action in actions:
                    if action not in result[entity]:
                        result[entity].append(action)

        # Добавляем личные права
        if self.extra_permissions:
            for entity, actions in self.extra_permissions.items():
                if entity not in result:
                    result[entity] = []
                for action in actions:
                    if action not in result[entity]:
                        result[entity].append(action)

        return result

    def has_group_access(self, entity: str) -> bool:
        """
        Проверка доступа к группе (модулю).

        Args:
            entity: Модуль (products, documents, delivery, ...)

        Returns:
            True, если есть хоть какое-то право на модуль
        """
        if self.is_superuser:
            return True

        # Проверяем личные права
        if self.extra_permissions and entity in self.extra_permissions:
            return bool(self.extra_permissions[entity])

        # Проверяем роли
        for role in self.roles:
            permissions = role.permissions or {}
            if entity in permissions and permissions[entity]:
                return True

        return False
