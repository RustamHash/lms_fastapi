"""Пресеты списков пользователя."""

from __future__ import annotations

from typing import Any

from sqlalchemy import Boolean, ForeignKey, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.infrastructure.orm_base import Base


class UserListPreset(Base):
    """Именованный пресет списка."""

    __tablename__ = "accounts_user_list_presets"
    __table_args__ = (
        UniqueConstraint("user_id", "table_id", "name", name="uq_user_preset_name"),
    )

    user_id: Mapped[int] = mapped_column(
        ForeignKey("accounts_user.id"), nullable=False, comment="Пользователь"
    )
    table_id: Mapped[str] = mapped_column(
        String(50), comment="Идентификатор сущности (entity_key)"
    )
    name: Mapped[str] = mapped_column(
        String(255), nullable=False, comment="Название пресета"
    )
    config: Mapped[dict[str, Any]] = mapped_column(
        JSONB, default=dict, comment="Конфигурация пресета"
    )
    is_default: Mapped[bool] = mapped_column(
        Boolean, default=False, comment="Пресет по умолчанию"
    )
