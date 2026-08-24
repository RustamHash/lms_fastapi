"""Схемы для поклажедателей, хранителей, перевозчиков."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field

from app.api.v1.base_schemas import BaseRead


class CarrierRead(BaseRead):
    legal_entity_id: int = Field(
        ...,
        title="Юрлицо",
        json_schema_extra={"ui_type": "select", "endpoint": "/api/v1/legal-entities"},
    )
    legal_entity: "LegalEntityRead | None" = Field(None, title="Юрлицо")
    model_config = ConfigDict(from_attributes=True)


class CarrierUpdate(BaseModel):
    legal_entity_id: int | None = Field(
        None,
        title="Юрлицо",
        json_schema_extra={"ui_type": "select", "endpoint": "/api/v1/legal-entities"},
    )


class CarrierCreate(BaseModel):
    legal_entity_id: int = Field(
        ...,
        title="Юрлицо",
        json_schema_extra={"ui_type": "select", "endpoint": "/api/v1/legal-entities"},
    )


class KeeperRead(BaseRead):
    legal_entity_id: int = Field(
        ...,
        title="Юрлицо",
        json_schema_extra={"ui_type": "select", "endpoint": "/api/v1/legal-entities"},
    )
    legal_entity: "LegalEntityRead | None" = Field(None, title="Юрлицо")
    model_config = ConfigDict(from_attributes=True)


class KeeperUpdate(BaseModel):
    legal_entity_id: int | None = Field(
        None,
        title="Юрлицо",
        json_schema_extra={"ui_type": "select", "endpoint": "/api/v1/legal-entities"},
    )


class KeeperCreate(BaseModel):
    legal_entity_id: int = Field(
        ...,
        title="Юрлицо",
        json_schema_extra={"ui_type": "select", "endpoint": "/api/v1/legal-entities"},
    )


class DepositorRead(BaseRead):
    legal_entity_id: int = Field(
        ...,
        title="Юрлицо",
        json_schema_extra={"ui_type": "select", "endpoint": "/api/v1/legal-entities"},
    )
    code: str = Field("", title="Код поклажедателя")
    legal_entity: "LegalEntityRead" = Field(..., title="Юрлицо")
    model_config = ConfigDict(from_attributes=True)


class DepositorCreate(BaseModel):
    legal_entity_id: int = Field(
        ...,
        title="Юрлицо",
        json_schema_extra={"ui_type": "select", "endpoint": "/api/v1/legal-entities"},
    )
    code: str = Field("", title="Код поклажедателя")


class DepositorUpdate(BaseModel):
    code: str | None = Field(None, title="Код поклажедателя")
    legal_entity_id: int | None = Field(
        None,
        title="Юрлицо",
        json_schema_extra={"ui_type": "select", "endpoint": "/api/v1/legal-entities"},
    )
