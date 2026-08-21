"""Заказы на доставку."""

from __future__ import annotations

from datetime import date, time

from sqlalchemy import Date, ForeignKey, String, Text, Time
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.infrastructure.orm_base import Base


class DeliveryOrder(Base):
    __tablename__ = "delivery_order"

    number: Mapped[str] = mapped_column(String(50), nullable=False, comment="Номер")
    contract_id: Mapped[int] = mapped_column(
        ForeignKey("parties_contract.id"), nullable=False, comment="Договор"
    )
    document_id: Mapped[int | None] = mapped_column(
        ForeignKey("documents_document.id"), nullable=True, comment="Документ склада"
    )
    parent_id: Mapped[int | None] = mapped_column(
        ForeignKey("delivery_order.id"), nullable=True, comment="Родительский заказ"
    )
    contact_person: Mapped[str] = mapped_column(String(255), default="", comment="Контактное лицо")
    phone: Mapped[str] = mapped_column(String(20), default="", comment="Телефон")
    delivery_date: Mapped[date | None] = mapped_column(Date, nullable=True, comment="Дата доставки")
    time_from: Mapped[time | None] = mapped_column(Time, nullable=True, comment="Время с")
    time_to: Mapped[time | None] = mapped_column(Time, nullable=True, comment="Время до")
    status: Mapped[str] = mapped_column(String(30), default="created", comment="Статус")
    is_edo: Mapped[bool] = mapped_column(default=False, comment="Признак ЭДО")
    comment: Mapped[str] = mapped_column(Text, default="", comment="Комментарий")

    contract: Mapped["Contract"] = relationship()
    document: Mapped["Document | None"] = relationship()
    deviations: Mapped[list["DeliveryDeviation"]] = relationship(back_populates="delivery_order")


class DeliveryDeviation(Base):
    __tablename__ = "delivery_deviation"

    delivery_order_id: Mapped[int] = mapped_column(
        ForeignKey("delivery_order.id"), nullable=False, comment="Заказ на доставку"
    )
    deviation_type: Mapped[str] = mapped_column(String(20), nullable=False, comment="Тип отклонения")
    quantity: Mapped[int] = mapped_column(default=0, comment="Количество мест")
    description: Mapped[str] = mapped_column(Text, default="", comment="Описание")

    delivery_order: Mapped["DeliveryOrder"] = relationship(back_populates="deviations")
