"""Возвраты товара."""

from __future__ import annotations

from datetime import date
from decimal import Decimal

from sqlalchemy import Date, ForeignKey, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.infrastructure.orm_base import Base


class ReturnOrder(Base):
    """Возврат товара от клиента."""

    __tablename__ = "orders_return"

    outbound_order_id: Mapped[int] = mapped_column(
        ForeignKey("orders_outbound.id"), nullable=False, comment="Исходный исходящий заказ"
    )
    inbound_order_id: Mapped[int | None] = mapped_column(
        ForeignKey("orders_inbound.id"), nullable=True, comment="Созданный приходный заказ"
    )
    depositor_id: Mapped[int] = mapped_column(
        ForeignKey("parties_depositor.id"), nullable=False, comment="Поклажедатель"
    )
    warehouse_id: Mapped[int | None] = mapped_column(
        ForeignKey("warehouse_warehouse.id"), nullable=True, comment="Склад"
    )
    customer_code: Mapped[str] = mapped_column(
        String(100), default="", comment="Код клиента"
    )
    customer_name: Mapped[str] = mapped_column(
        String(255), default="", comment="Наименование клиента"
    )
    return_date: Mapped[date] = mapped_column(Date, nullable=False, comment="Дата возврата")
    return_type: Mapped[str] = mapped_column(
        String(20), default="partial", comment="Тип возврата: full, partial"
    )
    status: Mapped[str] = mapped_column(
        String(50), default="new", comment="Статус возврата"
    )
    notes: Mapped[str] = mapped_column(Text, default="", comment="Примечания")

    lines: Mapped[list["ReturnOrderLine"]] = relationship(back_populates="return_order")


class ReturnOrderLine(Base):
    """Строка возврата."""

    __tablename__ = "orders_return_line"

    return_order_id: Mapped[int] = mapped_column(
        ForeignKey("orders_return.id"), nullable=False, comment="Возврат"
    )
    outbound_order_line_id: Mapped[int | None] = mapped_column(
        ForeignKey("orders_outbound_line.id"), nullable=True, comment="Исходная строка"
    )
    product_id: Mapped[int] = mapped_column(
        ForeignKey("warehouse_product.id"), nullable=False, comment="Товар"
    )
    qty_returned: Mapped[Decimal] = mapped_column(
        Numeric(10, 3), nullable=False, comment="Количество возвращаемого товара"
    )
    batch_number: Mapped[str] = mapped_column(
        String(100), default="", comment="Партия"
    )
    manufacture_date: Mapped[date | None] = mapped_column(
        Date, nullable=True, comment="Дата производства"
    )
    reason: Mapped[str] = mapped_column(
        Text, default="", comment="Причина возврата"
    )

    return_order: Mapped["ReturnOrder"] = relationship(back_populates="lines")
    product: Mapped["Product"] = relationship()
