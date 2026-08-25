"""Схемы журнала импорта."""

from __future__ import annotations

from typing import Any

from pydantic import Field, field_validator

from app.api.v1.base_schemas import BaseRead


class IntegrationLogRead(BaseRead):
    task_id: str = Field(..., title="Задача")
    profile_id: int | None = Field(None, title="Профиль")
    status: str = Field(..., title="Статус")
    document_type: str | None = Field(None, title="Тип документа")
    total_rows: int = Field(0, title="Всего")
    processed_rows: int = Field(0, title="Обработано")
    success_rows: int = Field(0, title="Успешно")
    error_rows: int = Field(0, title="Ошибок")
    messages: list[str] = Field(default_factory=list, title="Сообщения")
    errors: list[str] = Field(default_factory=list, title="Ошибки")
    current_step: str = Field("", title="Шаг")
    order_number: str = Field("", title="Номер заказа")
    file_id: int | None = Field(None, title="Файл ошибок")

    @field_validator("messages", "errors", mode="before")
    @classmethod
    def none_to_list(cls, value: Any) -> list[str]:
        return value or []
