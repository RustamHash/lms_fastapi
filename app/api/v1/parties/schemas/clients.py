"""Схемы для клиентов."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field

from app.api.v1.base_schemas import BaseRead


class ClientRead(BaseRead):
    depositor_id: int = Field(
        ...,
        title="Поклажедатель",
        json_schema_extra={"ui_type": "select", "endpoint": "/api/v1/depositors"},
    )
    code: str = Field(..., title="Код клиента")
    name: str = Field(..., title="Наименование")
    legal_name: str = Field("", title="Полное наименование")
    inn: str = Field("", title="ИНН")
    kpp: str = Field("", title="КПП")
    legal_address_id: int | None = Field(
        None,
        title="Юридический адрес",
        json_schema_extra={"ui_type": "select", "endpoint": "/api/v1/addresses"},
    )
    delivery_address_id: int | None = Field(
        None,
        title="Адрес доставки",
        json_schema_extra={"ui_type": "select", "endpoint": "/api/v1/addresses"},
    )
    is_edo: bool = Field(False, title="Признак ЭДО")
    depositor: "DepositorRead | None" = Field(None, title="Поклажедатель")
    legal_address: "AddressRead | None" = Field(None, title="Юридический адрес")
    delivery_address: "AddressRead | None" = Field(None, title="Адрес доставки")
    model_config = ConfigDict(from_attributes=True)


class ClientCreate(BaseModel):
    depositor_id: int = Field(
        ...,
        title="Поклажедатель",
        json_schema_extra={"ui_type": "select", "endpoint": "/api/v1/depositors"},
    )
    code: str = Field(..., title="Код клиента", min_length=1, max_length=50)
    name: str = Field(..., title="Наименование", min_length=1, max_length=255)
    legal_name: str = Field("", title="Полное наименование")
    inn: str = Field("", title="ИНН")
    kpp: str = Field("", title="КПП")
    legal_address_id: int | None = Field(
        None,
        title="Юридический адрес",
        json_schema_extra={"ui_type": "select", "endpoint": "/api/v1/addresses"},
    )
    delivery_address_id: int | None = Field(
        None,
        title="Адрес доставки",
        json_schema_extra={"ui_type": "select", "endpoint": "/api/v1/addresses"},
    )
    is_edo: bool = Field(False, title="Признак ЭДО")


class ClientUpdate(BaseModel):
    name: str | None = Field(None, title="Наименование")
    legal_name: str | None = Field(None, title="Полное наименование")
    inn: str | None = Field(None, title="ИНН")
    kpp: str | None = Field(None, title="КПП")
    legal_address_id: int | None = Field(
        None,
        title="Юридический адрес",
        json_schema_extra={"ui_type": "select", "endpoint": "/api/v1/addresses"},
    )
    delivery_address_id: int | None = Field(
        None,
        title="Адрес доставки",
        json_schema_extra={"ui_type": "select", "endpoint": "/api/v1/addresses"},
    )
    is_edo: bool | None = Field(None, title="Признак ЭДО")
