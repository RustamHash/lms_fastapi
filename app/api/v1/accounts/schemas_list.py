"""Схемы для настроек списков и пресетов."""

from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class ListPrefs(BaseModel):
    """Настройки списка."""

    order: list[str] = Field(default_factory=list)
    hidden: list[str] = Field(default_factory=list)
    widths: dict[str, int] = Field(default_factory=dict)
    filters: dict[str, str] = Field(default_factory=dict)
    exclude_filters: dict[str, list[str]] = Field(default_factory=dict)
    sort: dict[str, Any] | None = None
    quick_filters: list[str] = Field(default_factory=list)


class TableSettingsRead(BaseModel):
    """Ответ API — обёртка prefs."""

    prefs: ListPrefs


class TableSettingsUpdate(BaseModel):
    """Обновление настроек таблицы."""

    prefs: ListPrefs


class PresetRead(BaseModel):
    """Пресет списка."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    config: dict[str, Any] = Field(default_factory=dict)
    is_default: bool = False
    created_at: datetime
    updated_at: datetime


class PresetCreate(BaseModel):
    """Создание пресета."""

    name: str = Field(min_length=1, max_length=255)
    config: dict[str, Any] = Field(default_factory=dict)
    is_default: bool = False


class PresetUpdate(BaseModel):
    """Обновление пресета."""

    name: str | None = Field(default=None, min_length=1, max_length=255)
    config: dict[str, Any] | None = None
    is_default: bool | None = None
