"""Схемы для файлов."""

from __future__ import annotations

from app.api.v1.base_schemas import BaseRead


class FileRead(BaseRead):
    file_path: str
    file_type: str
    original_name: str
    size: int
    mime_type: str = ""
    uploaded_by_id: int | None = None
