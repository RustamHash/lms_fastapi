"""Схемы для модуля accounts."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class UserRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    username: str
    phone: str = ""
    email: str = ""
    is_superuser: bool = False
    is_active: bool = True


class UserCreate(BaseModel):
    username: str = Field(min_length=1, max_length=64)
    password: str = Field(min_length=8, max_length=128)
    phone: str = ""
    email: str = ""


class UserUpdate(BaseModel):
    phone: str | None = None
    email: str | None = None
    is_active: bool | None = None


class RoleRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    code: str
    permissions: dict = Field(default_factory=dict)


class RoleCreate(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    code: str = Field(min_length=1, max_length=50)
    permissions: dict = Field(default_factory=dict)


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class LoginRequest(BaseModel):
    username: str
    password: str


class AuditRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int | None
    action: str
    entity_type: str
    entity_id: str | None
    changes: dict = Field(default_factory=dict)
    created_at: str


class TableSettingsData(BaseModel):
    """Данные настроек таблицы."""

    order: list[str] = Field(default_factory=list)
    hidden: list[str] = Field(default_factory=list)
    widths: dict[str, int] = Field(default_factory=dict)


class TableSettingsRead(BaseModel):
    """Ответ API — обёртка prefs."""

    prefs: TableSettingsData | None = None


class TableSettingsUpdate(BaseModel):
    """Обновление настроек таблицы."""

    order: list[str] = Field(default_factory=list)
    hidden: list[str] = Field(default_factory=list)
    widths: dict[str, int] = Field(default_factory=dict)
