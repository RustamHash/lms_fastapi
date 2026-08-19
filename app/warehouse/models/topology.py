"""Топология склада."""

from __future__ import annotations

from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.infrastructure.orm_base import Base


class Warehouse(Base):
    """Физический склад."""

    __tablename__ = "warehouse_warehouse"

    name: Mapped[str] = mapped_column(String(255), nullable=False, comment="Название")
    address_id: Mapped[int | None] = mapped_column(
        ForeignKey("parties_address.id"), nullable=True, comment="Адрес"
    )

    address: Mapped["Address | None"] = relationship()
    virtual_warehouses: Mapped[list["VirtualWarehouse"]] = relationship(back_populates="warehouse")
    zones: Mapped[list["Zone"]] = relationship(back_populates="warehouse")


class VirtualWarehouse(Base):
    """Виртуальный склад поклажедателя."""

    __tablename__ = "warehouse_virtual_warehouse"

    depositor_id: Mapped[int] = mapped_column(
        ForeignKey("parties_depositor.id"), nullable=False, comment="Поклажедатель"
    )
    warehouse_id: Mapped[int] = mapped_column(
        ForeignKey("warehouse_warehouse.id"), nullable=False, comment="Физический склад"
    )
    code: Mapped[str] = mapped_column(String(50), nullable=False, comment="Код")
    name: Mapped[str] = mapped_column(String(255), nullable=False, comment="Наименование")

    depositor: Mapped["Depositor"] = relationship()
    warehouse: Mapped["Warehouse"] = relationship(back_populates="virtual_warehouses")


class Zone(Base):
    """Зона склада."""

    __tablename__ = "warehouse_zone"

    warehouse_id: Mapped[int] = mapped_column(
        ForeignKey("warehouse_warehouse.id"), nullable=False, comment="Склад"
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False, comment="Название")
    zone_type: Mapped[str] = mapped_column(String(20), nullable=False, comment="Тип зоны")

    warehouse: Mapped["Warehouse"] = relationship(back_populates="zones")
    rows: Mapped[list["Row"]] = relationship(back_populates="zone")


class Row(Base):
    """Ряд."""

    __tablename__ = "warehouse_row"

    zone_id: Mapped[int] = mapped_column(
        ForeignKey("warehouse_zone.id"), nullable=False, comment="Зона"
    )
    code: Mapped[str] = mapped_column(String(10), nullable=False, comment="Код ряда")
    row_type: Mapped[str] = mapped_column(String(20), nullable=False, comment="Тип ряда")

    zone: Mapped["Zone"] = relationship(back_populates="rows")
    locations: Mapped[list["Location"]] = relationship(back_populates="row")


class Location(Base):
    """Место в ряду."""

    __tablename__ = "warehouse_location"

    row_id: Mapped[int] = mapped_column(
        ForeignKey("warehouse_row.id"), nullable=False, comment="Ряд"
    )
    position: Mapped[int] = mapped_column(nullable=False, comment="Позиция")
    level: Mapped[int] = mapped_column(default=1, nullable=False, comment="Ярус")
    max_weight: Mapped[float | None] = mapped_column(nullable=True, comment="Макс. вес")
    max_volume: Mapped[float | None] = mapped_column(nullable=True, comment="Макс. объём")

    row: Mapped["Row"] = relationship(back_populates="locations")
