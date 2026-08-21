"""Настройки таблиц пользователя."""

from __future__ import annotations

from typing import Any

from sqlalchemy import ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.infrastructure.orm_base import Base


class UserTableSettings(Base):
    """Настройки таблиц пользователя."""

    __tablename__ = "accounts_user_table_settings"
    __table_args__ = (
        UniqueConstraint("user_id", "table_id", name="uq_user_table_settings"),
    )

    user_id: Mapped[int] = mapped_column(
        ForeignKey("accounts_user.id"), nullable=False, comment="Пользователь"
    )
    table_id: Mapped[str] = mapped_column(
        String(50), comment="Идентификатор сущности (entity_key)"
    )
    columns_order: Mapped[list[str]] = mapped_column(
        JSONB, default=list, comment="Порядок колонок"
    )
    hidden_columns: Mapped[list[str]] = mapped_column(
        JSONB, default=list, comment="Скрытые колонки"
    )
    column_widths: Mapped[dict[str, int]] = mapped_column(
        JSONB, default=dict, comment="Ширины колонок"
    )
    page_size: Mapped[int] = mapped_column(
        Integer, default=50, comment="Размер страницы"
    )
    default_ordering: Mapped[str] = mapped_column(
        String(50), default="-created_at", comment="Сортировка"
    )
    filters: Mapped[dict[str, str]] = mapped_column(
        JSONB, default=dict, comment="Фильтры"
    )
    exclude_filters: Mapped[dict[str, list[str]]] = mapped_column(
        JSONB, default=dict, comment="Исключения фильтров"
    )
    sort: Mapped[dict[str, Any] | None] = mapped_column(
        JSONB, nullable=True, comment="Сортировка (column, direction)"
    )
    quick_filters: Mapped[list[str]] = mapped_column(
        JSONB, default=list, comment="Быстрые фильтры"
    )
