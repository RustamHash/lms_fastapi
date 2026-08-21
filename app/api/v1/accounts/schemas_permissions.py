"""Схемы для управления правами."""

from __future__ import annotations

from pydantic import BaseModel, Field


class UserPermissionsRead(BaseModel):
    """Права пользователя."""

    user_id: int
    permissions: dict[str, list[str]] = Field(default_factory=dict)
    is_superuser: bool = False
    extra_permissions: dict[str, list[str]] = Field(default_factory=dict)


class UserPermissionsUpdate(BaseModel):
    """Обновление extra_permissions пользователя."""

    extra_permissions: dict[str, list[str]] = Field(default_factory=dict)


class AvailablePermissionsRead(BaseModel):
    """Список доступных модулей и действий."""

    modules: list[str] = Field(default_factory=list)
    actions: list[str] = Field(default_factory=list)
