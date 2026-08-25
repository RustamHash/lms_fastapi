"""Остатки."""

from __future__ import annotations

from decimal import Decimal

from sqlalchemy import CheckConstraint, ForeignKey, Index, Numeric, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.infrastructure.orm_base import Base


class StockBalance(Base):
    """Остаток товара в ячейке на LPN."""

    __tablename__ = "warehouse_stock_balance"
    __table_args__ = (
        UniqueConstraint(
            "product_id",
            "location_id",
            "batch_id",
            "lpn_id",
            name="uq_stock_balance_key",
        ),
        CheckConstraint("quantity >= 0", name="ck_stock_balance_quantity_non_negative"),
        CheckConstraint("reserved_quantity >= 0", name="ck_stock_balance_reserved_non_negative"),
        CheckConstraint(
            "reserved_quantity <= quantity",
            name="ck_stock_balance_reserved_le_quantity",
        ),
        Index("ix_stock_balance_product_location", "product_id", "location_id"),
    )

    product_id: Mapped[int] = mapped_column(
        ForeignKey("warehouse_product.id"), nullable=False, comment="Товар"
    )
    location_id: Mapped[int] = mapped_column(
        ForeignKey("warehouse_location.id"), nullable=False, comment="Ячейка"
    )
    lpn_id: Mapped[int] = mapped_column(
        ForeignKey("warehouse_lpn.id"), nullable=False, comment="LPN"
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
    lpn: Mapped["LPN"] = relationship(back_populates="stock_balances")
    batch: Mapped["Batch"] = relationship(back_populates="stock_balances")
