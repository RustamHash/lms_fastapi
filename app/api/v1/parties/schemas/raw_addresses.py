"""Схемы для сырых адресов (алиасов)."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field

from app.api.v1.base_schemas import BaseRead


class AliasCreate(BaseModel):
    raw_text: str = Field(..., title="Сырой адрес", min_length=1)
    source: str = Field("", title="Источник")


class AliasUpdate(BaseModel):
    raw_text: str | None = Field(None, title="Сырой адрес")
    source: str | None = Field(None, title="Источник")
    normalized_address_id: int | None = Field(
        None,
        title="Нормализованный адрес",
        json_schema_extra={"ui_type": "select", "endpoint": "/api/v1/addresses"},
    )


class RawAddressCreate(BaseModel):
    raw_text: str = Field(..., title="Сырой адрес", min_length=1)
    source: str = Field("", title="Источник")


class RawAddressUpdate(BaseModel):
    raw_text: str | None = Field(None, title="Сырой адрес")
    source: str | None = Field(None, title="Источник")
    normalized_address_id: int | None = Field(
        None,
        title="Нормализованный адрес",
        json_schema_extra={"ui_type": "select", "endpoint": "/api/v1/addresses"},
    )


class RawAddressRead(BaseRead):
    raw_text: str = Field(..., title="Сырой адрес")
    hash: str = Field(..., title="SHA256")
    normalized_address_id: int = Field(
        ...,
        title="Нормализованный адрес",
        json_schema_extra={"ui_type": "select", "endpoint": "/api/v1/addresses"},
    )
    source: str = Field("", title="Источник")
    normalized_address: "AddressRead | None" = Field(None, title="Нормализованный адрес")
    model_config = ConfigDict(from_attributes=True)
