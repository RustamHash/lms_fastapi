"""Привязка пользователя к торговой точке."""

from __future__ import annotations

from sqlalchemy import ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.infrastructure.orm_base import Base


class UserTradePoint(Base):
    """Пользователь имеет доступ к торговой точке."""

    __tablename__ = "accounts_user_trade_point"
    __table_args__ = (
        UniqueConstraint("user_id", "trade_point_id", name="uq_user_trade_point"),
    )

    user_id: Mapped[int] = mapped_column(
        ForeignKey("accounts_user.id"), nullable=False, comment="Пользователь"
    )
    trade_point_id: Mapped[int] = mapped_column(
        ForeignKey("parties_trade_point.id"), nullable=False, comment="Торговая точка"
    )
