"""Упаковка товара."""

from __future__ import annotations

from decimal import Decimal

from sqlalchemy import Boolean, ForeignKey, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.infrastructure.orm_base import Base


class Package(Base):
    """Упаковка."""

    __tablename__ = "warehouse_package"

    product_id: Mapped[int] = mapped_column(
        ForeignKey("warehouse_product.id"), nullable=False, comment="Товар"
    )
    name: Mapped[str] = mapped_column(String(100), nullable=False, comment="Название")
    quantity: Mapped[int] = mapped_column(nullable=False, comment="Количество в упаковке")
    barcode: Mapped[str | None] = mapped_column(String(50), unique=True, nullable=True, comment="Штрихкод")
    weight: Mapped[Decimal | None] = mapped_column(Numeric(10, 3), nullable=True, comment="Вес брутто")
    width: Mapped[Decimal | None] = mapped_column(Numeric(10, 2), nullable=True, comment="Ширина")
    height: Mapped[Decimal | None] = mapped_column(Numeric(10, 2), nullable=True, comment="Высота")
    depth: Mapped[Decimal | None] = mapped_column(Numeric(10, 2), nullable=True, comment="Глубина")
    is_base_unit: Mapped[bool] = mapped_column(Boolean, default=False, comment="Базовая единица")

    product: Mapped["Product"] = relationship(back_populates="packages")
