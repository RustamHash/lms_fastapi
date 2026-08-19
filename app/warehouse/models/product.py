"""Товары."""

from __future__ import annotations

from decimal import Decimal

from sqlalchemy import Boolean, ForeignKey, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.infrastructure.orm_base import Base


class ProductGroup(Base):
    """Группа товара."""

    __tablename__ = "warehouse_product_group"

    name: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, comment="Название")

    products: Mapped[list["Product"]] = relationship(back_populates="group")


class Product(Base):
    """Товар."""

    __tablename__ = "warehouse_product"

    depositor_id: Mapped[int] = mapped_column(
        ForeignKey("parties_depositor.id"), nullable=False, comment="Поклажедатель"
    )
    group_id: Mapped[int | None] = mapped_column(
        ForeignKey("warehouse_product_group.id"), nullable=True, comment="Группа"
    )
    external_id: Mapped[str] = mapped_column(String(255), nullable=False, comment="Внешний код")
    sku: Mapped[str] = mapped_column(String(100), default="", comment="Артикул")
    name: Mapped[str] = mapped_column(String(255), nullable=False, comment="Наименование")
    legal_name: Mapped[str] = mapped_column(String(255), default="", comment="Полное наименование")
    weight: Mapped[Decimal] = mapped_column(Numeric(10, 3), nullable=False, comment="Вес нетто")
    volume: Mapped[Decimal] = mapped_column(Numeric(10, 3), nullable=False, comment="Объём")
    price: Mapped[Decimal | None] = mapped_column(Numeric(12, 2), nullable=True, comment="Цена")
    shelf_life_days: Mapped[int | None] = mapped_column(nullable=True, comment="Срок годности")
    min_shelf_life_days: Mapped[int | None] = mapped_column(nullable=True, comment="Мин. срок")
    is_marked: Mapped[bool] = mapped_column(Boolean, default=False, comment="Маркированный")
    is_serial_tracked: Mapped[bool] = mapped_column(Boolean, default=False, comment="Серийный учёт")
    is_batch_tracked: Mapped[bool] = mapped_column(Boolean, default=False, comment="Партионный учёт")
    is_expiration_tracked: Mapped[bool] = mapped_column(Boolean, default=False, comment="Сроки годности")
    temperature_requirements: Mapped[str] = mapped_column(String(50), default="", comment="Темп. режим")

    depositor: Mapped["Depositor"] = relationship()
    group: Mapped[ProductGroup | None] = relationship(back_populates="products")
    packages: Mapped[list["Package"]] = relationship(back_populates="product")
    batches: Mapped[list["Batch"]] = relationship(back_populates="product")
