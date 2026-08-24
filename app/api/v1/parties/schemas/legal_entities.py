"""Схемы для юрлиц."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field

from app.api.v1.base_schemas import BaseRead


class LegalEntityRead(BaseRead):
    name: str = Field(..., title="Краткое наименование")
    legal_name: str = Field("", title="Полное наименование")
    inn: str = Field("", title="ИНН")
    kpp: str = Field("", title="КПП")
    ogrn: str = Field("", title="ОГРН")
    legal_address_id: int | None = Field(
        None,
        title="Юридический адрес",
        json_schema_extra={"ui_type": "select", "endpoint": "/api/v1/addresses"},
    )
    actual_address_id: int | None = Field(
        None,
        title="Фактический адрес",
        json_schema_extra={"ui_type": "select", "endpoint": "/api/v1/addresses"},
    )
    phone: str = Field("", title="Телефон")
    email: str = Field("", title="Email")
    edo_uuid: str | None = Field(None, title="Идентификатор ЭДО")
    legal_address: "AddressRead | None" = Field(None, title="Юридический адрес")
    actual_address: "AddressRead | None" = Field(None, title="Фактический адрес")
    model_config = ConfigDict(from_attributes=True)


class LegalEntityCreate(BaseModel):
    name: str = Field(..., title="Краткое наименование", min_length=1, max_length=255)
    legal_name: str = Field("", title="Полное наименование")
    inn: str = Field("", title="ИНН", max_length=12)
    kpp: str = Field("", title="КПП", max_length=9)
    ogrn: str = Field("", title="ОГРН", max_length=15)
    legal_address_id: int | None = Field(
        None,
        title="Юридический адрес",
        json_schema_extra={"ui_type": "select", "endpoint": "/api/v1/addresses"},
    )
    actual_address_id: int | None = Field(
        None,
        title="Фактический адрес",
        json_schema_extra={"ui_type": "select", "endpoint": "/api/v1/addresses"},
    )
    phone: str = Field("", title="Телефон")
    email: str = Field("", title="Email")
    edo_uuid: str | None = Field(None, title="Идентификатор ЭДО")


class LegalEntityUpdate(BaseModel):
    name: str | None = Field(None, title="Краткое наименование")
    legal_name: str | None = Field(None, title="Полное наименование")
    inn: str | None = Field(None, title="ИНН")
    kpp: str | None = Field(None, title="КПП")
    ogrn: str | None = Field(None, title="ОГРН")
    legal_address_id: int | None = Field(
        None,
        title="Юридический адрес",
        json_schema_extra={"ui_type": "select", "endpoint": "/api/v1/addresses"},
    )
    actual_address_id: int | None = Field(
        None,
        title="Фактический адрес",
        json_schema_extra={"ui_type": "select", "endpoint": "/api/v1/addresses"},
    )
    phone: str | None = Field(None, title="Телефон")
    email: str | None = Field(None, title="Email")
    edo_uuid: str | None = Field(None, title="Идентификатор ЭДО")
