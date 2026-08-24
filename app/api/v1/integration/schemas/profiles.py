"""Схемы для профилей интеграции."""

from __future__ import annotations

from pydantic import BaseModel, Field

from app.api.v1.base_schemas import BaseRead


class IntegrationProfileRead(BaseRead):
    depositor_id: int = Field(
        ...,
        title="Поклажедатель",
        json_schema_extra={"ui_type": "select", "endpoint": "/api/v1/depositors"},
    )
    name: str = Field(..., title="Название")
    source_type: str = Field(..., title="Тип источника")
    config: dict = Field(default_factory=dict, title="Настройки")


class IntegrationProfileCreate(BaseModel):
    depositor_id: int = Field(
        ...,
        title="Поклажедатель",
        json_schema_extra={"ui_type": "select", "endpoint": "/api/v1/depositors"},
    )
    name: str = Field(..., title="Название")
    source_type: str = Field(..., title="Тип источника")
    config: dict = Field(default_factory=dict, title="Настройки")
