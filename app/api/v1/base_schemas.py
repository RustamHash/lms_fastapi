"""Базовые схемы для API."""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class BaseRead(BaseModel):
    """Базовая схема для чтения — все поля модели."""

    model_config = ConfigDict(from_attributes=True)

    id: int = Field(..., title="ID")
    is_active: bool = Field(True, title="Активна")
    is_deleted: bool = Field(False, title="Удалена")
    created_at: datetime = Field(..., title="Создана")
    updated_at: datetime = Field(..., title="Обновлена")
    created_by_id: int | None = Field(None, title="Создал")
    updated_by_id: int | None = Field(None, title="Изменил")
    deleted_at: datetime | None = Field(None, title="Удалена (когда)")
    deleted_by_id: int | None = Field(None, title="Удалил")
