"""Схемы для договоров."""

from __future__ import annotations

from datetime import date

from pydantic import BaseModel, ConfigDict, Field

from app.api.v1.base_schemas import BaseRead


class ContractRead(BaseRead):
    number: str = Field(..., title="Номер договора")
    customer_id: int = Field(
        ...,
        title="Заказчик",
        json_schema_extra={"ui_type": "select", "endpoint": "/api/v1/legal-entities"},
    )
    executor_id: int = Field(
        ...,
        title="Исполнитель",
        json_schema_extra={"ui_type": "select", "endpoint": "/api/v1/legal-entities"},
    )
    contract_type: str = Field(..., title="Тип договора")
    start_date: date = Field(..., title="Дата начала")
    end_date: date | None = Field(None, title="Дата окончания")
    status: str = Field("active", title="Статус")
    terms: dict = Field(default_factory=dict, title="Условия")
    customer: "LegalEntityRead | None" = Field(None, title="Заказчик")
    executor: "LegalEntityRead | None" = Field(None, title="Исполнитель")
    model_config = ConfigDict(from_attributes=True)


class ContractCreate(BaseModel):
    number: str = Field(..., title="Номер договора", min_length=1, max_length=50)
    customer_id: int = Field(
        ...,
        title="Заказчик",
        json_schema_extra={"ui_type": "select", "endpoint": "/api/v1/legal-entities"},
    )
    executor_id: int = Field(
        ...,
        title="Исполнитель",
        json_schema_extra={"ui_type": "select", "endpoint": "/api/v1/legal-entities"},
    )
    contract_type: str = Field(..., title="Тип договора")
    start_date: date = Field(..., title="Дата начала")
    end_date: date | None = Field(None, title="Дата окончания")
    terms: dict = Field(default_factory=dict, title="Условия")


class ContractUpdate(BaseModel):
    number: str | None = Field(None, title="Номер договора")
    end_date: date | None = Field(None, title="Дата окончания")
    status: str | None = Field(None, title="Статус")
    terms: dict | None = Field(None, title="Условия")
