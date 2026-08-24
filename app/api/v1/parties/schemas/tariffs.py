"""Схемы для тарифов."""

from __future__ import annotations

from datetime import date as date_type
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field

from app.api.v1.base_schemas import BaseRead


class TariffDocumentRead(BaseRead):
    contract_id: int = Field(
        ...,
        title="Договор",
        json_schema_extra={"ui_type": "select", "endpoint": "/api/v1/contracts"},
    )
    document_type: str = Field(..., title="Тип документа")
    number: str = Field(..., title="Номер")
    document_date: date_type = Field(..., title="Дата подписания")
    valid_from: date_type = Field(..., title="Действует с")
    valid_until: date_type | None = Field(None, title="Действует до")
    currency: str = Field("RUB", title="Валюта")
    vat_rate: str = Field("20", title="Ставка НДС")
    contract: "ContractRead | None" = Field(None, title="Договор")
    model_config = ConfigDict(from_attributes=True)


class TariffDocumentCreate(BaseModel):
    contract_id: int = Field(
        ...,
        title="Договор",
        json_schema_extra={"ui_type": "select", "endpoint": "/api/v1/contracts"},
    )
    document_type: str = Field(..., title="Тип документа")
    number: str = Field(..., title="Номер")
    document_date: date_type = Field(..., title="Дата подписания")
    valid_from: date_type = Field(..., title="Действует с")
    valid_until: date_type | None = Field(None, title="Действует до")
    currency: str = Field("RUB", title="Валюта")
    vat_rate: str = Field("20", title="Ставка НДС")


class TariffDocumentUpdate(BaseModel):
    number: str | None = Field(None, title="Номер")
    document_date: date_type | None = Field(None, title="Дата документа")
    valid_from: date_type | None = Field(None, title="Действует с")
    valid_until: date_type | None = Field(None, title="Действует до")
    currency: str | None = Field(None, title="Валюта")
    vat_rate: str | None = Field(None, title="Ставка НДС")


class TariffRead(BaseRead):
    document_id: int = Field(
        ...,
        title="Тарифный документ",
        json_schema_extra={"ui_type": "select", "endpoint": "/api/v1/tariff-documents"},
    )
    service_group: str = Field(..., title="Группа услуг")
    name: str = Field(..., title="Название")
    description: str = Field("", title="Описание")
    unit: str = Field(..., title="Единица измерения")
    price: Decimal = Field(..., title="Цена")
    document: "TariffDocumentRead | None" = Field(None, title="Тарифный документ")
    model_config = ConfigDict(from_attributes=True)


class TariffCreate(BaseModel):
    document_id: int = Field(
        ...,
        title="Тарифный документ",
        json_schema_extra={"ui_type": "select", "endpoint": "/api/v1/tariff-documents"},
    )
    service_group: str = Field(..., title="Группа услуг")
    name: str = Field(..., title="Название")
    description: str = Field("", title="Описание")
    unit: str = Field(..., title="Единица измерения")
    price: Decimal = Field(..., title="Цена")


class TariffUpdate(BaseModel):
    name: str | None = Field(None, title="Название")
    description: str | None = Field(None, title="Описание")
    unit: str | None = Field(None, title="Единица измерения")
    price: Decimal | None = Field(None, title="Цена")
    service_group: str | None = Field(None, title="Группа услуг")
