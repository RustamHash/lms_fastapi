"""Модель аудита."""

from __future__ import annotations

from typing import Any

from sqlalchemy import ForeignKey, String
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.infrastructure.orm_base import Base


class Audit(Base):
    """Журнал действий пользователей."""

    __tablename__ = "accounts_audit"

    user_id: Mapped[int | None] = mapped_column(
        ForeignKey("accounts_user.id"), nullable=True, comment="Пользователь"
    )
    action: Mapped[str] = mapped_column(String(20), comment="Действие")
    entity_type: Mapped[str] = mapped_column(String(100), comment="Тип сущности")
    entity_id: Mapped[str | None] = mapped_column(
        String(36), nullable=True, comment="ID сущности"
    )
    changes: Mapped[dict[str, Any]] = mapped_column(
        JSONB, default=dict, comment="Изменения"
    )
    ip_address: Mapped[str] = mapped_column(String(45), default="", comment="IP адрес")
    user_agent: Mapped[str] = mapped_column(
        String(500), default="", comment="User Agent"
    )
