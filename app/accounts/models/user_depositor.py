"""Привязка пользователя к поклажедателю."""

from __future__ import annotations

from sqlalchemy import ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.infrastructure.orm_base import Base


class UserDepositor(Base):
    """Пользователь имеет доступ к поклажедателю."""

    __tablename__ = "accounts_user_depositor"
    __table_args__ = (
        UniqueConstraint("user_id", "depositor_id", name="uq_user_depositor"),
    )

    user_id: Mapped[int] = mapped_column(
        ForeignKey("accounts_user.id"), nullable=False, comment="Пользователь"
    )
    depositor_id: Mapped[int] = mapped_column(
        ForeignKey("parties_depositor.id"), nullable=False, comment="Поклажедатель"
    )
