"""LPN — логистическая единица."""

from __future__ import annotations

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.infrastructure.orm_base import Base


class LPN(Base):
    """Паллета с этикеткой."""

    __tablename__ = "warehouse_lpn"

    number: Mapped[str] = mapped_column(String(20), unique=True, comment="Номер паллета")
    status: Mapped[str] = mapped_column(String(20), default="created", comment="Статус")

    stock_balances: Mapped[list["StockBalance"]] = relationship(back_populates="lpn")
    movements: Mapped[list["StockMovement"]] = relationship(back_populates="lpn")
