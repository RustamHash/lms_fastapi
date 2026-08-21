"""Правила уведомлений."""

from __future__ import annotations

from sqlalchemy import Boolean, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from app.infrastructure.orm_base import Base


class NotificationRule(Base):
    """Правило: при событии отправить уведомление через канал."""

    __tablename__ = "notifications_rule"

    event_type: Mapped[str] = mapped_column(
        String(100), nullable=False, comment="Тип события"
    )
    channel: Mapped[str] = mapped_column(
        String(20), nullable=False, comment="Канал: app, email"
    )
    recipient_type: Mapped[str] = mapped_column(
        String(30), nullable=False, comment="Тип получателя: user, role"
    )
    recipient_id: Mapped[int | None] = mapped_column(
        ForeignKey("accounts_user.id"),
        nullable=True,
        comment="ID пользователя (если recipient_type=user)",
    )
    role_code: Mapped[str | None] = mapped_column(
        ForeignKey("accounts_role.code"),
        nullable=True,
        comment="Код роли (если recipient_type=role)",
    )
    is_active: Mapped[bool] = mapped_column(
        Boolean, default=True, comment="Правило активно"
    )
