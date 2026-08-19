"""Модель файла."""

from __future__ import annotations

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from app.infrastructure.orm_base import Base


class File(Base):
    """Файл: фото, документы, импорт/экспорт."""

    __tablename__ = "files"

    file_path: Mapped[str] = mapped_column(String(500), comment="Путь к файлу")
    file_type: Mapped[str] = mapped_column(String(30), comment="Тип файла")
    original_name: Mapped[str] = mapped_column(String(255), comment="Исходное имя")
    size: Mapped[int] = mapped_column(comment="Размер (байт)")
    mime_type: Mapped[str] = mapped_column(String(100), default="", comment="MIME тип")
    uploaded_by_id: Mapped[int | None] = mapped_column(
        nullable=True, comment="Кем загружен"
    )

    def __repr__(self) -> str:
        return f"<File(id={self.id}, name={self.original_name})>"
