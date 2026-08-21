"""Входящие заказы (заявки на приёмку)."""

from __future__ import annotations

from datetime import date
from decimal import Decimal

from sqlalchemy import Boolean, Date, ForeignKey, Numeric, String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy import UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.parties.models import Client
from app.warehouse.models import Warehouse

from app.infrastructure.orm_base import Base
from app.core.statuses import OrderStatus


class InboundOrder(Base):
    """Заявка на приёмку товара."""

    __tablename__ = "orders_inbound"
    __table_args__ = (
        UniqueConstraint("depositor_id", "number", name="uq_inbound_depositor_number"),
    )

    depositor_id: Mapped[int] = mapped_column(
        ForeignKey("parties_depositor.id"), nullable=False, comment="Поклажедатель"
    )
    warehouse_id: Mapped[int | None] = mapped_column(
        ForeignKey("warehouse_warehouse.id"), nullable=True, comment="Склад"
    )
    number: Mapped[str] = mapped_column(
        String(100), nullable=False, comment="Номер заявки"
    )
    supplier_code: Mapped[str] = mapped_column(
        String(100), default="", comment="Код поставщика"
    )
    supplier_id: Mapped[int | None] = mapped_column(
        ForeignKey("parties_client.id"), nullable=True, comment="Поставщик"
    )
    order_date: Mapped[date] = mapped_column(Date, nullable=False, comment="Дата заявки")
    planned_date: Mapped[date | None] = mapped_column(
        Date, nullable=True, comment="Планируемая дата приёмки"
    )
    notes: Mapped[str] = mapped_column(Text, default="", comment="Примечания")
    status: Mapped[str] = mapped_column(
        String(50), default=OrderStatus.NEW.value, comment="Статус заявки"
    )
    pordrsp_exported: Mapped[bool] = mapped_column(
        Boolean, default=False, comment="Отклик pordrsp выгружен"
    )
    recadv_exported: Mapped[bool] = mapped_column(
        Boolean, default=False, comment="Подтверждение recadv выгружено"
    )
    has_shortage: Mapped[bool] = mapped_column(
        Boolean, default=False, comment="Есть недогруз"
    )

    lines: Mapped[list["InboundOrderLine"]] = relationship(back_populates="order")
    depositor: Mapped["Depositor"] = relationship()
    warehouse: Mapped["Warehouse | None"] = relationship()
    supplier: Mapped["Client | None"] = relationship(foreign_keys=[supplier_id])


class InboundOrderLine(Base):
    """Строка заявки на приёмку."""

    __tablename__ = "orders_inbound_line"

    order_id: Mapped[int] = mapped_column(
        ForeignKey("orders_inbound.id"), nullable=False, comment="Заявка"
    )
    product_id: Mapped[int | None] = mapped_column(
        ForeignKey("warehouse_product.id"), nullable=True, comment="Товар"
    )
    quantity: Mapped[Decimal] = mapped_column(
        Numeric(10, 3), nullable=False, comment="Количество"
    )
    batch_number: Mapped[str] = mapped_column(
        String(100), default="", comment="Номер партии"
    )
    manufacture_date: Mapped[date | None] = mapped_column(
        Date, nullable=True, comment="Дата изготовления"
    )
    serial_numbers: Mapped[list] = mapped_column(
        JSONB, default=list, comment="Серийные номера"
    )

    order: Mapped["InboundOrder"] = relationship(back_populates="lines")
    product: Mapped["Product | None"] = relationship()
