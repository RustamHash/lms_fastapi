"""Профиль интеграции и журнал импорта."""

from __future__ import annotations

from typing import Any
from uuid import uuid4

from sqlalchemy import Boolean, ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.infrastructure.orm_base import Base
from app.parties.models.counterparty import Depositor
from app.files.models import File


class IntegrationProfile(Base):
    """Профиль интеграции."""

    __tablename__ = "integration_profile"

    depositor_id: Mapped[int] = mapped_column(
        ForeignKey("parties_depositor.id"), nullable=False, comment="Поклажедатель"
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False, comment="Название")
    source_type: Mapped[str] = mapped_column(
        String(20), nullable=False, comment="Тип источника"
    )
    config: Mapped[dict[str, Any]] = mapped_column(
        JSONB, default=dict, comment="Настройки"
    )

    depositor: Mapped["Depositor"] = relationship(lazy="selectin")
    logs: Mapped[list["IntegrationLog"]] = relationship(back_populates="profile")


class IntegrationLog(Base):
    """Журнал импорта с прогрессом."""

    __tablename__ = "integration_log"

    task_id: Mapped[str] = mapped_column(
        String(36), default=lambda: str(uuid4()), comment="UUID задачи импорта"
    )
    profile_id: Mapped[int | None] = mapped_column(
        ForeignKey("integration_profile.id"),
        nullable=True,
        comment="Профиль (если импорт по одному)",
    )
    status: Mapped[str] = mapped_column(
        String(20),
        default="starting",
        comment="Статус: starting, processing, completed, failed",
    )
    document_type: Mapped[str | None] = mapped_column(
        String(20), nullable=True, comment="Тип: porder, order, all"
    )
    total_rows: Mapped[int] = mapped_column(Integer, default=0, comment="Всего файлов")
    processed_rows: Mapped[int] = mapped_column(
        Integer, default=0, comment="Обработано файлов"
    )
    success_rows: Mapped[int] = mapped_column(Integer, default=0, comment="Успешно")
    error_rows: Mapped[int] = mapped_column(Integer, default=0, comment="С ошибками")
    messages: Mapped[list[str]] = mapped_column(
        JSONB, default=list, comment="Лог сообщений"
    )
    errors: Mapped[list[str]] = mapped_column(JSONB, default=list, comment="Ошибки")
    current_step: Mapped[str] = mapped_column(
        String(255), default="", comment="Текущий шаг"
    )
    order_number: Mapped[str] = mapped_column(
        String(100), default="", comment="Текущий номер заказа"
    )
    file_id: Mapped[int | None] = mapped_column(
        ForeignKey("files.id"), nullable=True, comment="Файл с ошибками (Excel)"
    )

    profile: Mapped["IntegrationProfile | None"] = relationship(back_populates="logs")


class IntegrationError(Base):
    """Ошибка импорта."""

    __tablename__ = "integration_error"

    log_id: Mapped[int] = mapped_column(
        ForeignKey("integration_log.id"), nullable=False, comment="Журнал"
    )
    row_number: Mapped[int] = mapped_column(Integer, default=0, comment="Номер строки")
    error_message: Mapped[str] = mapped_column(
        String, default="", comment="Сообщение об ошибке"
    )
    raw_data: Mapped[dict[str, Any]] = mapped_column(
        JSONB, default=dict, comment="Исходные данные"
    )

    log: Mapped["IntegrationLog"] = relationship()
