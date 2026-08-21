"""Схемы для модуля integration."""

from __future__ import annotations

from pydantic import BaseModel, Field

from app.api.v1.base_schemas import BaseRead


class IntegrationProfileRead(BaseRead):
    depositor_id: int
    name: str
    source_type: str
    config: dict = Field(default_factory=dict)


class IntegrationProfileCreate(BaseModel):
    depositor_id: int
    name: str
    source_type: str
    config: dict = Field(default_factory=dict)


class IntegrationLogRead(BaseRead):
    profile_id: int
    status: str
    total_rows: int = 0
    success_rows: int = 0
    error_rows: int = 0
    error_details: dict = Field(default_factory=dict)
    file_id: int | None = None


class IntegrationErrorRead(BaseRead):
    log_id: int
    row_number: int
    error_message: str
    raw_data: dict = Field(default_factory=dict)
