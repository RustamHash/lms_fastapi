"""Уведомления."""

from __future__ import annotations

from sqlalchemy import ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.infrastructure.orm_base import Base


class Notification(Base):
    __tablename__ = "notifications_notification"

    user_id: Mapped[int] = mapped_column(
        ForeignKey("accounts_user.id"), nullable=False, comment="Получатель"
    )
    title: Mapped[str] = mapped_column(String(255), nullable=False, comment="Заголовок")
    text: Mapped[str] = mapped_column(Text, nullable=False, comment="Текст")
    notification_type: Mapped[str] = mapped_column(
        String(20), default="system", comment="Тип уведомления"
    )
    status: Mapped[str] = mapped_column(String(20), default="pending", comment="Статус")
    link: Mapped[str] = mapped_column(String(500), default="", comment="Ссылка")
    sent_at: Mapped[str | None] = mapped_column(String(50), nullable=True, comment="Когда отправлено")
    read_at: Mapped[str | None] = mapped_column(String(50), nullable=True, comment="Когда прочитано")

    user: Mapped["User"] = relationship(foreign_keys=[user_id], lazy="selectin")
