"""Водители и транспорт."""

from __future__ import annotations

from decimal import Decimal

from sqlalchemy import ForeignKey, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.infrastructure.orm_base import Base


class Driver(Base):
    __tablename__ = "delivery_driver"

    name: Mapped[str] = mapped_column(String(255), nullable=False, comment="ФИО")
    phone: Mapped[str] = mapped_column(String(20), default="", comment="Телефон")
    carrier_id: Mapped[int | None] = mapped_column(
        ForeignKey("parties_carrier.id"), nullable=True, comment="Перевозчик"
    )

    carrier: Mapped["Carrier | None"] = relationship(lazy="selectin")
    routes: Mapped[list["Route"]] = relationship(back_populates="driver")


class Vehicle(Base):
    __tablename__ = "delivery_vehicle"

    number: Mapped[str] = mapped_column(String(20), nullable=False, comment="Гос. номер")
    brand: Mapped[str] = mapped_column(String(100), default="", comment="Марка")
    model: Mapped[str] = mapped_column(String(100), default="", comment="Модель")
    capacity: Mapped[Decimal | None] = mapped_column(Numeric(10, 2), nullable=True, comment="Грузоподъёмность")
    volume: Mapped[Decimal | None] = mapped_column(Numeric(10, 2), nullable=True, comment="Объём")
    carrier_id: Mapped[int | None] = mapped_column(
        ForeignKey("parties_carrier.id"), nullable=True, comment="Перевозчик"
    )

    carrier: Mapped["Carrier | None"] = relationship(lazy="selectin")
    routes: Mapped[list["Route"]] = relationship(back_populates="vehicle")
