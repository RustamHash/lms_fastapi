"""Схемы для управления правами."""

from __future__ import annotations

from pydantic import BaseModel, Field, field_validator

from app.accounts.permissions_catalog import validate_permissions_map


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
        return validate_permissions_map(v)


class AvailablePermissionsRead(BaseModel):
    """Список доступных модулей и действий."""

    modules: list[str] = Field(default_factory=list)
    actions: list[str] = Field(default_factory=list)
    module_labels: dict[str, str] = Field(default_factory=dict)
    action_labels: dict[str, str] = Field(default_factory=dict)
