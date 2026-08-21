"""Базовые схемы для API."""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict


class BaseRead(BaseModel):
    """Базовая схема для чтения — все поля модели."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    is_active: bool = True
    is_deleted: bool = False
    created_at: datetime
    updated_at: datetime
    created_by_id: int | None = None
    updated_by_id: int | None = None
    deleted_at: datetime | None = None
    deleted_by_id: int | None = None
