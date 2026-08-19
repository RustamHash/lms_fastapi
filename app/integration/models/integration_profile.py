"""Профиль интеграции."""

from __future__ import annotations

from typing import Any

from sqlalchemy import ForeignKey, String
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.infrastructure.orm_base import Base


class IntegrationProfile(Base):
    __tablename__ = "integration_profile"

    depositor_id: Mapped[int] = mapped_column(
        ForeignKey("parties_depositor.id"), nullable=False, comment="Поклажедатель"
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False, comment="Название")
    source_type: Mapped[str] = mapped_column(String(20), nullable=False, comment="Тип источника")
    config: Mapped[dict[str, Any]] = mapped_column(JSONB, default=dict, comment="Настройки")

    depositor: Mapped["Depositor"] = relationship()
    logs: Mapped[list["IntegrationLog"]] = relationship(back_populates="profile")


class IntegrationLog(Base):
    __tablename__ = "integration_log"

    profile_id: Mapped[int] = mapped_column(
        ForeignKey("integration_profile.id"), nullable=False, comment="Профиль"
    )
    status: Mapped[str] = mapped_column(String(20), default="pending", comment="Статус")
    total_rows: Mapped[int] = mapped_column(default=0, comment="Всего строк")
    success_rows: Mapped[int] = mapped_column(default=0, comment="Успешно")
    error_rows: Mapped[int] = mapped_column(default=0, comment="С ошибками")
    error_details: Mapped[dict[str, Any]] = mapped_column(JSONB, default=dict, comment="Детали ошибок")
    file_id: Mapped[int | None] = mapped_column(
        ForeignKey("files.id"), nullable=True, comment="Файл"
    )

    profile: Mapped["IntegrationProfile"] = relationship(back_populates="logs")


class IntegrationError(Base):
    __tablename__ = "integration_error"

    log_id: Mapped[int] = mapped_column(
        ForeignKey("integration_log.id"), nullable=False, comment="Журнал"
    )
    row_number: Mapped[int] = mapped_column(nullable=False, comment="Номер строки")
    error_message: Mapped[str] = mapped_column(comment="Сообщение об ошибке")
    raw_data: Mapped[dict[str, Any]] = mapped_column(JSONB, default=dict, comment="Исходные данные")

    log: Mapped["IntegrationLog"] = relationship()
