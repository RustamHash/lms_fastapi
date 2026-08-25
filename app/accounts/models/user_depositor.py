"""Привязка пользователя к поклажедателю."""

from __future__ import annotations

from sqlalchemy import ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import TYPE_CHECKING

from app.infrastructure.orm_base import Base

if TYPE_CHECKING:
    from app.accounts.models.user import User
    from app.parties.models.counterparty import Depositor


class UserDepositor(Base):
    """Пользователь имеет доступ к поклажедателю."""

    __tablename__ = "accounts_user_depositor"
    __table_args__ = (
        UniqueConstraint("user_id", "depositor_id", name="uq_user_depositor"),
    )

    user_id: Mapped[int] = mapped_column(
        ForeignKey("accounts_user.id", ondelete="CASCADE"),
        nullable=False,
        comment="Пользователь",
    )
    depositor_id: Mapped[int] = mapped_column(
        ForeignKey("parties_depositor.id", ondelete="CASCADE"),
        nullable=False,
        comment="Поклажедатель",
    )

    user: Mapped["User"] = relationship(
        back_populates="user_depositors",
        foreign_keys=[user_id],
    )
    depositor: Mapped["Depositor"] = relationship(foreign_keys=[depositor_id])
