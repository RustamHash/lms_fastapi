"""Привязка пользователя к клиенту (торговый агент)."""

from __future__ import annotations

from sqlalchemy import ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import TYPE_CHECKING

from app.infrastructure.orm_base import Base

if TYPE_CHECKING:
    from app.accounts.models.user import User
    from app.parties.models.client import Client


class UserClient(Base):
    """Пользователь имеет доступ к клиенту."""

    __tablename__ = "accounts_user_client"
    __table_args__ = (
        UniqueConstraint("user_id", "client_id", name="uq_user_client"),
    )

    user_id: Mapped[int] = mapped_column(
        ForeignKey("accounts_user.id", ondelete="CASCADE"),
        nullable=False,
        comment="Пользователь",
    )
    client_id: Mapped[int] = mapped_column(
        ForeignKey("parties_client.id", ondelete="CASCADE"),
        nullable=False,
        comment="Клиент",
    )

    user: Mapped["User"] = relationship(
        back_populates="user_clients",
        foreign_keys=[user_id],
    )
    client: Mapped["Client"] = relationship(foreign_keys=[client_id])
