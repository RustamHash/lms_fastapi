"""Схемы для управления правами."""

from __future__ import annotations

from pydantic import BaseModel, Field, field_validator


class UserPermissionsRead(BaseModel):
    """Права пользователя."""

    user_id: int
    permissions: dict[str, list[str]] = Field(default_factory=dict)
    is_superuser: bool = False
    extra_permissions: dict[str, list[str]] = Field(default_factory=dict)


class UserPermissionsUpdate(BaseModel):
    """Обновление extra_permissions пользователя."""

    extra_permissions: dict[str, list[str]] = Field(default_factory=dict)

    @field_validator("extra_permissions")
    @classmethod
    def validate_permissions(cls, v: dict[str, list[str]]) -> dict[str, list[str]]:
        """Проверяет, что entity и action валидны."""
        from app.api.v1.accounts.routes_permissions import AVAILABLE_MODULES, AVAILABLE_ACTIONS
        
        for entity, actions in v.items():
            if entity not in AVAILABLE_MODULES:
                raise ValueError(f"Неизвестный модуль: {entity}")
            for action in actions:
                if action not in AVAILABLE_ACTIONS:
                    raise ValueError(f"Неизвестное действие: {action} для модуля {entity}")
        return v


class AvailablePermissionsRead(BaseModel):
    """Список доступных модулей и действий."""

    modules: list[str] = Field(default_factory=list)
    actions: list[str] = Field(default_factory=list)
