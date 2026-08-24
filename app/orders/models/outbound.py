"""Исходящие заказы (заявки на отгрузку)."""

from __future__ import annotations

from datetime import date
from decimal import Decimal
from uuid import uuid4

from sqlalchemy import Boolean, Date, ForeignKey, Integer, Numeric, String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy import UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.infrastructure.orm_base import Base
from app.core.statuses import OrderStatus, DeliveryStatus


class OutboundOrder(Base):
    """Заявка на отгрузку товара."""

    __tablename__ = "orders_outbound"
    __table_args__ = (
        UniqueConstraint("depositor_id", "number", name="uq_outbound_depositor_number"),
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
    customer_code: Mapped[str] = mapped_column(
        String(100), default="", comment="Код клиента"
    )
    customer_name: Mapped[str] = mapped_column(
        String(255), default="", comment="Наименование клиента"
    )
    client_id: Mapped[int | None] = mapped_column(
        ForeignKey("parties_client.id"), nullable=True, comment="Клиент"
    )
    delivery_address_name: Mapped[str] = mapped_column(
        String(255), default="", comment="Адрес доставки"
    )
    order_date: Mapped[date] = mapped_column(
        Date, nullable=False, comment="Дата заявки"
    )
    shipping_date: Mapped[date | None] = mapped_column(
        Date, nullable=True, comment="Планируемая дата отгрузки"
    )
    needs_delivery: Mapped[bool] = mapped_column(
        Boolean, default=False, comment="Нужна доставка"
    )
    delivery_only: Mapped[bool] = mapped_column(
        Boolean, default=False, comment="Только доставка (без склада)"
    )
    places_count: Mapped[int | None] = mapped_column(
        nullable=True, comment="Количество мест"
    )
    declared_weight: Mapped[Decimal | None] = mapped_column(
        Numeric(12, 3), nullable=True, comment="Заявленный вес, кг"
    )
    delivery_contact: Mapped[str] = mapped_column(
        String(255), default="", comment="Контакт для доставки"
    )
    notes: Mapped[str] = mapped_column(Text, default="", comment="Примечания")
    status: Mapped[str] = mapped_column(
        String(50), default=OrderStatus.NEW.value, comment="Статус заявки"
    )
    ordrsp_exported: Mapped[bool] = mapped_column(
        Boolean, default=False, comment="Отклик ordrsp выгружен"
    )
    desadv_exported: Mapped[bool] = mapped_column(
        Boolean, default=False, comment="Уведомление desadv выгружено"
    )
    zone_id: Mapped[int | None] = mapped_column(
        ForeignKey("parties_delivery_zone.id"), nullable=True, comment="Зона доставки"
    )
    document_number: Mapped[str] = mapped_column(
        String(100), default="", comment="Номер документа"
    )
    is_printed: Mapped[bool] = mapped_column(
        Boolean, default=False, comment="Документы распечатаны"
    )
    uuid: Mapped[str] = mapped_column(
        String(36), default=lambda: str(uuid4()), unique=True, comment="UUID для QR"
    )
    delivery_status: Mapped[str | None] = mapped_column(
        String(20), nullable=True, comment="Статус доставки"
    )
    is_edo: Mapped[bool] = mapped_column(
        Boolean, nullable=False, server_default="false", default=False, comment="Признак ЭДО"
    )
    address_comment: Mapped[str] = mapped_column(
        String(255), nullable=False, server_default="", default="", comment="Комментарий к адресу"
    )
    shipping_contact: Mapped[str] = mapped_column(
        String(255), nullable=False, server_default="", default="", comment="Контакт для доставки"
    )
    total_quantity: Mapped[int] = mapped_column(
        Integer, nullable=False, server_default="0", default=0, comment="Общее количество штук"
    )

    lines: Mapped[list["OutboundOrderLine"]] = relationship(back_populates="order")
    depositor: Mapped["Depositor"] = relationship(lazy="selectin")
    client: Mapped["Client | None"] = relationship(lazy="selectin")
    warehouse: Mapped["Warehouse | None"] = relationship(lazy="selectin")


class OutboundOrderLine(Base):
    """Строка заявки на отгрузку."""

    __tablename__ = "orders_outbound_line"

    order_id: Mapped[int] = mapped_column(
        ForeignKey("orders_outbound.id"), nullable=False, comment="Заявка"
    )
    product_id: Mapped[int | None] = mapped_column(
        ForeignKey("warehouse_product.id"), nullable=True, comment="Товар"
    )
    quantity: Mapped[Decimal] = mapped_column(
        Numeric(10, 3), nullable=False, comment="Количество"
    )
    location_id: Mapped[int | None] = mapped_column(
        ForeignKey("warehouse_location.id"), nullable=True, comment="Ячейка"
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

    order: Mapped["OutboundOrder"] = relationship(back_populates="lines")
    product: Mapped["Product | None"] = relationship()
    location: Mapped["Location | None"] = relationship()
