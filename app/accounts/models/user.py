"""Модель пользователя."""

from __future__ import annotations

from sqlalchemy import Boolean, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

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

    roles: Mapped[list["Role"]] = relationship(
        secondary="accounts_user_roles",
        back_populates="users",
    )

    def has_permission(self, permission: str) -> bool:
        """Проверка права. Формат: 'action:entity', например 'create:legal_entities'."""
        if self.is_superuser:
            return True
        
        action, entity = permission.split(":", 1)
        
        for role in self.roles:
            permissions = role.permissions or {}
            
            # Проверяем общий доступ
            if permissions.get("all") == True:
                return True
            
            # Проверяем действие
            action_perms = permissions.get(f"can_{action}", [])
            if entity in action_perms:
                return True
        
        return False

    def get_permissions(self) -> dict:
        """Все права пользователя."""
        if self.is_superuser:
            return {"all": True}
        
        result = {"all": False}
        for role in self.roles:
            permissions = role.permissions or {}
            for key, value in permissions.items():
                if key == "all":
                    continue
                if key not in result:
                    result[key] = []
                if isinstance(value, list):
                    result[key].extend(value)
        
        return result
