"""Схемы для файлов."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict


class FileRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    file_path: str
    file_type: str
    original_name: str
    size: int
    mime_type: str = ""
    uploaded_by_id: int | None = None
