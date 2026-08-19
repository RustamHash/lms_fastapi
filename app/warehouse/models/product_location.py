"""Связь товара с ячейкой отбора."""

from __future__ import annotations

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.infrastructure.orm_base import Base


class ProductLocation(Base):
    """Товар-ячейка отбора."""

    __tablename__ = "warehouse_product_location"

    product_id: Mapped[int] = mapped_column(
        ForeignKey("warehouse_product.id"), nullable=False, comment="Товар"
    )
    location_id: Mapped[int] = mapped_column(
        ForeignKey("warehouse_location.id"), nullable=False, comment="Ячейка отбора"
    )

    product: Mapped["Product"] = relationship()
    location: Mapped["Location"] = relationship()
