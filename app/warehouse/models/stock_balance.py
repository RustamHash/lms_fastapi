"""Остатки."""

from __future__ import annotations

from decimal import Decimal

from sqlalchemy import ForeignKey, Numeric
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.infrastructure.orm_base import Base


class StockBalance(Base):
    """Остаток товара в ячейке."""

    __tablename__ = "warehouse_stock_balance"

    product_id: Mapped[int] = mapped_column(
        ForeignKey("warehouse_product.id"), nullable=False, comment="Товар"
    )
    location_id: Mapped[int] = mapped_column(
        ForeignKey("warehouse_location.id"), nullable=False, comment="Ячейка"
    )
    lpn_id: Mapped[int | None] = mapped_column(
        ForeignKey("warehouse_lpn.id"), nullable=True, comment="LPN"
    )
    batch_id: Mapped[int] = mapped_column(
        ForeignKey("warehouse_batch.id"), nullable=False, comment="Партия"
    )
    quantity: Mapped[Decimal] = mapped_column(Numeric(20, 3), nullable=False, comment="Количество")
    reserved_quantity: Mapped[Decimal] = mapped_column(
        Numeric(20, 3), default=Decimal("0"), comment="Зарезервировано"
    )

    product: Mapped["Product"] = relationship()
    location: Mapped["Location"] = relationship()
    lpn: Mapped["LPN | None"] = relationship(back_populates="stock_balances")
    batch: Mapped["Batch"] = relationship(back_populates="stock_balances")
