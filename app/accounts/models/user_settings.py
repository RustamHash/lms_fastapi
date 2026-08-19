"""Настройки интерфейса пользователя."""

from __future__ import annotations

from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from app.infrastructure.orm_base import Base


class UserSettings(Base):
    """Настройки интерфейса пользователя."""

    __tablename__ = "accounts_user_settings"

    user_id: Mapped[int] = mapped_column(
        ForeignKey("accounts_user.id"),
        unique=True,
        nullable=False,
        comment="Пользователь",
    )
    menu_style: Mapped[str] = mapped_column(
        String(10), default="top", comment="Стиль меню"
    )
    theme: Mapped[str] = mapped_column(String(10), default="light", comment="Тема")
    density: Mapped[str] = mapped_column(
        String(15), default="compact", comment="Плотность"
    )
    font_size: Mapped[str] = mapped_column(
        String(10), default="small", comment="Размер шрифта"
    )
