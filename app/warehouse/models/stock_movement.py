"""Движения товара."""

from __future__ import annotations

from decimal import Decimal

from sqlalchemy import ForeignKey, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.infrastructure.orm_base import Base


class StockMovement(Base):
    """Движение."""

    __tablename__ = "warehouse_stock_movement"

    product_id: Mapped[int] = mapped_column(
        ForeignKey("warehouse_product.id"), nullable=False, comment="Товар"
    )
    document_id: Mapped[int | None] = mapped_column(
        ForeignKey("documents_document.id"), nullable=True, comment="Документ"
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
    direction: Mapped[str] = mapped_column(String(10), nullable=False, comment="Направление")
    quantity: Mapped[Decimal] = mapped_column(Numeric(20, 3), nullable=False, comment="Количество")

    product: Mapped["Product"] = relationship()
    location: Mapped["Location"] = relationship()
    lpn: Mapped["LPN | None"] = relationship(back_populates="movements")
    batch: Mapped["Batch"] = relationship(back_populates="movements")
