"""Схемы для адресов и зон доставки."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field

from app.api.v1.base_schemas import BaseRead


class DeliveryZoneRead(BaseRead):
    name: str = Field(..., title="Название")
    model_config = ConfigDict(from_attributes=True)


class DeliveryZoneUpdate(BaseModel):
    name: str | None = Field(None, title="Название")


class DeliveryZoneCreate(BaseModel):
    name: str = Field(..., title="Название", min_length=1, max_length=255)


class AddressRead(BaseRead):
    full_address: str = Field(..., title="Полный адрес")
    region: str = Field("", title="Регион")
    city: str = Field("", title="Город")
    street: str = Field("", title="Улица")
    house: str = Field("", title="Дом")
    building: str = Field("", title="Корпус")
    structure: str = Field("", title="Строение")
    flat: str = Field("", title="Квартира")
    fias_id: str = Field("", title="FIAS ID")
    latitude: float | None = Field(None, title="Широта")
    longitude: float | None = Field(None, title="Долгота")
    postal_code: str = Field("", title="Индекс")
    delivery_zone_id: int | None = Field(
        None,
        title="Зона доставки",
        json_schema_extra={"ui_type": "select", "endpoint": "/api/v1/delivery-zones"},
    )
    delivery_zone: "DeliveryZoneRead | None" = Field(None, title="Зона доставки")
    model_config = ConfigDict(from_attributes=True)


class AddressCreate(BaseModel):
    full_address: str = Field(..., title="Полный адрес", min_length=1, max_length=500)
    region: str = Field("", title="Регион", max_length=255)
    city: str = Field("", title="Город", max_length=255)
    street: str = Field("", title="Улица", max_length=255)
    house: str = Field("", title="Дом", max_length=64)
    building: str = Field("", title="Корпус", max_length=32)
    structure: str = Field("", title="Строение", max_length=32)
    flat: str = Field("", title="Квартира", max_length=32)
    fias_id: str = Field("", title="FIAS ID", max_length=36)
    latitude: float | None = Field(None, title="Широта", ge=-90, le=90)
    longitude: float | None = Field(None, title="Долгота", ge=-180, le=180)
    postal_code: str = Field("", title="Индекс", max_length=10)
    delivery_zone_id: int | None = Field(
        None,
        title="Зона доставки",
        json_schema_extra={"ui_type": "select", "endpoint": "/api/v1/delivery-zones"},
    )


class AddressResolve(BaseModel):
    raw_text: str = Field(..., title="Сырой адрес", min_length=1)
    source: str = Field("", title="Источник")


class AddressUpdate(BaseModel):
    full_address: str | None = Field(None, title="Полный адрес")
    region: str | None = Field(None, title="Регион")
    city: str | None = Field(None, title="Город")
    street: str | None = Field(None, title="Улица")
    house: str | None = Field(None, title="Дом")
    building: str | None = Field(None, title="Корпус")
    structure: str | None = Field(None, title="Строение")
    flat: str | None = Field(None, title="Квартира")
    fias_id: str | None = Field(None, title="FIAS ID")
    latitude: float | None = Field(None, title="Широта")
    longitude: float | None = Field(None, title="Долгота")
    postal_code: str | None = Field(None, title="Индекс")
    delivery_zone_id: int | None = Field(
        None,
        title="Зона доставки",
        json_schema_extra={"ui_type": "select", "endpoint": "/api/v1/delivery-zones"},
    )
