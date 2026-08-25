"""Схемы для модуля accounts."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.accounts.permissions_catalog import validate_permissions_map
from app.api.v1.base_schemas import BaseRead


class RoleBrief(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    code: str
    name: str


class UserRead(BaseRead):
    username: str
    phone: str = ""
    email: str | None = None
    is_superuser: bool = False
    roles: list[RoleBrief] = Field(default_factory=list)
    depositor_ids: list[int] = Field(default_factory=list)
    client_ids: list[int] = Field(default_factory=list)

    @field_validator("roles", mode="before")
    @classmethod
    def _drop_deleted_roles(cls, value: object) -> object:
        if value is None:
            return []
        if isinstance(value, list):
            return [item for item in value if not getattr(item, "is_deleted", False)]
        return value


class UserCreate(BaseModel):
    username: str = Field(min_length=1, max_length=64)
    password: str = Field(min_length=8, max_length=128)
    phone: str = ""
    email: str | None = None


class UserUpdate(BaseModel):
    phone: str | None = None
    email: str | None = None
    is_active: bool | None = None


class UserRolesUpdate(BaseModel):
    role_ids: list[int] = Field(default_factory=list)


class UserDepositorsUpdate(BaseModel):
    depositor_ids: list[int] = Field(default_factory=list)


class UserClientsUpdate(BaseModel):
    client_ids: list[int] = Field(default_factory=list)


class MeRead(BaseModel):
    """Текущий пользователь.

    Пустой depositor_ids = все поклажедатели (сотрудник склада).
    Непустой depositor_ids без client_ids = менеджер поклажедателя.
    Непустой client_ids = торговый агент.
    """

    id: int
    username: str
    is_superuser: bool
    permissions: dict[str, list[str]] = Field(default_factory=dict)
    roles: list[RoleBrief] = Field(default_factory=list)
    depositor_ids: list[int] = Field(default_factory=list)
    client_ids: list[int] = Field(default_factory=list)


class RoleRead(BaseRead):
    name: str
    code: str
    permissions: dict = Field(default_factory=dict)


class RoleCreate(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    code: str = Field(min_length=1, max_length=50)
    permissions: dict[str, list[str]] = Field(default_factory=dict)

    @field_validator("permissions")
    @classmethod
    def _validate_permissions(cls, value: dict[str, list[str]]) -> dict[str, list[str]]:
        return validate_permissions_map(value)


class RoleUpdate(BaseModel):
    name: str | None = Field(None, min_length=1, max_length=100)
    code: str | None = Field(None, min_length=1, max_length=50)
    permissions: dict[str, list[str]] | None = None

    @field_validator("permissions")
    @classmethod
    def _validate_permissions(
        cls, value: dict[str, list[str]] | None
    ) -> dict[str, list[str]] | None:
        if value is None:
            return None
        return validate_permissions_map(value)


class RolePermissionsUpdate(BaseModel):
    permissions: dict[str, list[str]] = Field(default_factory=dict)

    @field_validator("permissions")
    @classmethod
    def _validate_permissions(cls, value: dict[str, list[str]]) -> dict[str, list[str]]:
        return validate_permissions_map(value)


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
