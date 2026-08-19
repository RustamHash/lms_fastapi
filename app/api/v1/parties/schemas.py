"""Схемы для модуля parties."""

from __future__ import annotations

from datetime import date
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


# ========== Адреса ==========

class DeliveryZoneRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str


class DeliveryZoneCreate(BaseModel):
    name: str = Field(min_length=1, max_length=255)


class AddressRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    full_address: str
    region: str = ""
    city: str = ""
    street: str = ""
    house: str = ""
    building: str = ""
    structure: str = ""
    flat: str = ""
    fias_id: str = ""
    latitude: Decimal | None = None
    longitude: Decimal | None = None
    postal_code: str = ""
    delivery_zone_id: int | None = None
    is_deleted: bool = False
    is_active: bool = True


class AddressResolve(BaseModel):
    raw_text: str = Field(min_length=1)
    source: str = ""


# ========== Юрлица ==========

class LegalEntityRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    legal_name: str = ""
    inn: str = ""
    kpp: str = ""
    ogrn: str = ""
    legal_address_id: int | None = None
    actual_address_id: int | None = None
    phone: str = ""
    email: str = ""
    edo_uuid: str | None = None


class LegalEntityCreate(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    legal_name: str = ""
    inn: str = Field(max_length=12)
    kpp: str = Field(max_length=9)
    ogrn: str = Field(max_length=15)
    legal_address_id: int | None = None
    actual_address_id: int | None = None
    phone: str = ""
    email: str = ""
    edo_uuid: str | None = None


class LegalEntityUpdate(BaseModel):
    name: str | None = None
    legal_name: str | None = None
    inn: str | None = None
    kpp: str | None = None
    ogrn: str | None = None
    legal_address_id: int | None = None
    actual_address_id: int | None = None
    phone: str | None = None
    email: str | None = None
    edo_uuid: str | None = None


# ========== Поклажедатели ==========

class DepositorRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    legal_entity_id: int
    code: str = ""
    legal_entity_name: str = ""


class DepositorCreate(BaseModel):
    legal_entity_id: int
    code: str = ""


# ========== Клиенты ==========

class ClientRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    depositor_id: int
    external_id: str
    name: str
    legal_name: str = ""
    inn: str = ""
    kpp: str = ""
    legal_address_id: int | None = None
    is_edo: bool = False


class ClientCreate(BaseModel):
    depositor_id: int
    external_id: str = Field(min_length=1, max_length=50)
    name: str = Field(min_length=1, max_length=255)
    legal_name: str = ""
    inn: str = ""
    kpp: str = ""
    legal_address_id: int | None = None
    is_edo: bool = False


class ClientUpdate(BaseModel):
    name: str | None = None
    legal_name: str | None = None
    inn: str | None = None
    kpp: str | None = None
    legal_address_id: int | None = None
    is_edo: bool | None = None


class TradePointRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    client_id: int
    address_id: int
    name: str = ""


class TradePointCreate(BaseModel):
    client_id: int
    address_id: int
    name: str = ""


# ========== Договоры ==========

class ContractRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    number: str
    customer_id: int
    executor_id: int
    contract_type: str
    start_date: date
    end_date: date | None = None
    status: str = "active"
    terms: dict = Field(default_factory=dict)


class ContractCreate(BaseModel):
    number: str = Field(min_length=1, max_length=50)
    customer_id: int
    executor_id: int
    contract_type: str
    start_date: date
    end_date: date | None = None
    terms: dict = Field(default_factory=dict)


# ========== Тарифы ==========

class TariffDocumentRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    contract_id: int
    document_type: str
    number: str
    date: date
    valid_from: date
    valid_until: date | None = None
    currency: str = "RUB"
    vat_rate: str = "20"


class TariffDocumentCreate(BaseModel):
    contract_id: int
    document_type: str
    number: str
    date: date
    valid_from: date
    valid_until: date | None = None
    currency: str = "RUB"
    vat_rate: str = "20"


class TariffRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    document_id: int
    service_group: str
    name: str
    description: str = ""
    unit: str
    price: Decimal


class TariffCreate(BaseModel):
    document_id: int
    service_group: str
    name: str
    description: str = ""
    unit: str
    price: Decimal


class RawAddressRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    raw_text: str
    hash: str
    normalized_address_id: int
    source: str = ""
    full_address: str | None = None
    is_deleted: bool = False


# ========== Update-схемы ==========

class LegalEntityUpdate(BaseModel):
    name: str | None = None
    legal_name: str | None = None
    inn: str | None = None
    kpp: str | None = None
    ogrn: str | None = None
    legal_address_id: int | None = None
    actual_address_id: int | None = None
    phone: str | None = None
    email: str | None = None
    edo_uuid: str | None = None


class AddressUpdate(BaseModel):
    full_address: str | None = None
    region: str | None = None
    city: str | None = None
    street: str | None = None
    house: str | None = None
    building: str | None = None
    structure: str | None = None
    flat: str | None = None
    fias_id: str | None = None
    latitude: Decimal | None = None
    longitude: Decimal | None = None
    postal_code: str | None = None
    delivery_zone_id: int | None = None


class DepositorUpdate(BaseModel):
    code: str | None = None
    legal_entity_id: int | None = None


class ClientUpdate(BaseModel):
    name: str | None = None
    legal_name: str | None = None
    inn: str | None = None
    kpp: str | None = None
    legal_address_id: int | None = None
    is_edo: bool | None = None


class TradePointUpdate(BaseModel):
    name: str | None = None
    client_id: int | None = None
    address_id: int | None = None


class ContractUpdate(BaseModel):
    number: str | None = None
    end_date: date | None = None
    status: str | None = None
    terms: dict | None = None


class TariffDocumentUpdate(BaseModel):
    number: str | None = None
    document_date: date | None = None
    valid_from: date | None = None
    valid_until: date | None = None
    currency: str | None = None
    vat_rate: str | None = None


class TariffUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    unit: str | None = None
    price: Decimal | None = None
    service_group: str | None = None
