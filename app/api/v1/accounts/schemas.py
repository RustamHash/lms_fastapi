"""Схемы для модуля accounts."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field

from app.api.v1.base_schemas import BaseRead


class UserRead(BaseRead):
    username: str
    phone: str = ""
    email: str = ""
    is_superuser: bool = False
    extra_permissions: dict = Field(default_factory=dict)


class UserCreate(BaseModel):
    username: str = Field(min_length=1, max_length=64)
    password: str = Field(min_length=8, max_length=128)
    phone: str = ""
    email: str = ""


class UserUpdate(BaseModel):
    phone: str | None = None
    email: str | None = None
    is_active: bool | None = None


class RoleRead(BaseRead):
    name: str
    code: str
    permissions: dict = Field(default_factory=dict)


class RoleCreate(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    code: str = Field(min_length=1, max_length=50)
    permissions: dict = Field(default_factory=dict)


class RolePermissionsUpdate(BaseModel):
    permissions: dict = Field(default_factory=dict)


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class LoginRequest(BaseModel):
    username: str
    password: str


class AuditRead(BaseRead):
    user_id: int | None
    action: str
    entity_type: str
    entity_id: str | None
    changes: dict = Field(default_factory=dict)
    ip_address: str = ""
    user_agent: str = ""


class AuditCreate(BaseModel):
    action: str
    entity_type: str
    entity_id: str | None = None
    changes: dict = Field(default_factory=dict)


class AuditUpdate(BaseModel):
    action: str | None = None
    entity_type: str | None = None
    entity_id: str | None = None
    changes: dict | None = None


class TableSettingsData(BaseModel):
    order: list[str] = Field(default_factory=list)
    hidden: list[str] = Field(default_factory=list)
    widths: dict[str, int] = Field(default_factory=dict)


class TableSettingsRead(BaseModel):
    prefs: TableSettingsData | None = None


class TableSettingsUpdate(BaseModel):
    order: list[str] = Field(default_factory=list)
    hidden: list[str] = Field(default_factory=list)
    widths: dict[str, int] = Field(default_factory=dict)
