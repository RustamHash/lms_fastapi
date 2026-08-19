"""Партия товара."""

from __future__ import annotations

from datetime import date

from sqlalchemy import Date, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.infrastructure.orm_base import Base


class Batch(Base):
    """Партия."""

    __tablename__ = "warehouse_batch"

    product_id: Mapped[int] = mapped_column(
        ForeignKey("warehouse_product.id"), nullable=False, comment="Товар"
    )
    batch_number: Mapped[str] = mapped_column(String(100), nullable=False, comment="Номер партии")
    production_date: Mapped[date | None] = mapped_column(Date, nullable=True, comment="Дата производства")
    expiration_date: Mapped[date | None] = mapped_column(Date, nullable=True, comment="Срок годности")

    product: Mapped["Product"] = relationship(back_populates="batches")
    stock_balances: Mapped[list["StockBalance"]] = relationship(back_populates="batch")
    movements: Mapped[list["StockMovement"]] = relationship(back_populates="batch")
