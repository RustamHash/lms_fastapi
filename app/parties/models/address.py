"""Адреса и зоны доставки."""

from __future__ import annotations

from decimal import Decimal

from sqlalchemy import ForeignKey, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.infrastructure.orm_base import Base


class DeliveryZone(Base):
    """Зона доставки."""

    __tablename__ = "parties_delivery_zone"

    name: Mapped[str] = mapped_column(
        String(255), unique=True, nullable=False, comment="Название"
    )

    addresses: Mapped[list["Address"]] = relationship(
        back_populates="delivery_zone"
    )

    def __repr__(self) -> str:
        return f"<DeliveryZone(id={self.id}, name={self.name})>"


class Address(Base):
    """Нормализованный адрес."""

    __tablename__ = "parties_address"

    full_address: Mapped[str] = mapped_column(
        Text, nullable=False, comment="Полный адрес"
    )
    region: Mapped[str] = mapped_column(String(255), default="", comment="Регион")
    city: Mapped[str] = mapped_column(String(255), default="", comment="Город")
    street: Mapped[str] = mapped_column(String(255), default="", comment="Улица")
    house: Mapped[str] = mapped_column(String(64), default="", comment="Дом")
    building: Mapped[str] = mapped_column(String(32), default="", comment="Корпус")
    structure: Mapped[str] = mapped_column(String(32), default="", comment="Строение")
    flat: Mapped[str] = mapped_column(String(32), default="", comment="Квартира")
    fias_id: Mapped[str] = mapped_column(String(36), default="", comment="FIAS ID")
    latitude: Mapped[Decimal | None] = mapped_column(
        Numeric(9, 6), nullable=True, comment="Широта"
    )
    longitude: Mapped[Decimal | None] = mapped_column(
        Numeric(9, 6), nullable=True, comment="Долгота"
    )
    postal_code: Mapped[str] = mapped_column(String(10), default="", comment="Индекс")
    delivery_zone_id: Mapped[int | None] = mapped_column(
        ForeignKey("parties_delivery_zone.id"), nullable=True, comment="Зона доставки"
    )

    delivery_zone: Mapped[DeliveryZone | None] = relationship(
        back_populates="addresses"
    )
    raw_addresses: Mapped[list["RawAddress"]] = relationship(
        back_populates="normalized_address"
    )

    def __repr__(self) -> str:
        return f"id={self.id}"


class RawAddress(Base):
    """Сырой адрес до нормализации."""

    __tablename__ = "parties_raw_address"

    raw_text: Mapped[str] = mapped_column(Text, nullable=False, comment="Сырой адрес")
    hash: Mapped[str] = mapped_column(
        String(64), unique=True, comment="SHA256 от нормализованного"
    )
    normalized_address_id: Mapped[int] = mapped_column(
        ForeignKey("parties_address.id"),
        nullable=False,
        comment="Нормализованный адрес",
    )
    source: Mapped[str] = mapped_column(String(50), default="", comment="Источник")

    normalized_address: Mapped[Address] = relationship(
        back_populates="raw_addresses"
    )

    def __repr__(self) -> str:
        return f"id={self.id}"
