"""Маршруты."""

from __future__ import annotations

from datetime import date, time

from sqlalchemy import Date, ForeignKey, Integer, String, Time
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.infrastructure.orm_base import Base


class Route(Base):
    __tablename__ = "delivery_route"

    number: Mapped[str] = mapped_column(String(50), nullable=False, comment="Номер")
    driver_id: Mapped[int] = mapped_column(
        ForeignKey("delivery_driver.id"), nullable=False, comment="Водитель"
    )
    vehicle_id: Mapped[int] = mapped_column(
        ForeignKey("delivery_vehicle.id"), nullable=False, comment="Автомобиль"
    )
    date: Mapped[date] = mapped_column(Date, nullable=False, comment="Дата")
    status: Mapped[str] = mapped_column(String(20), default="planned", comment="Статус")

    driver: Mapped["Driver"] = relationship(back_populates="routes")
    vehicle: Mapped["Vehicle"] = relationship(back_populates="routes")
    lines: Mapped[list["RouteLine"]] = relationship(back_populates="route")


class RouteLine(Base):
    __tablename__ = "delivery_route_line"

    route_id: Mapped[int] = mapped_column(
        ForeignKey("delivery_route.id"), nullable=False, comment="Маршрут"
    )
    delivery_order_id: Mapped[int] = mapped_column(
        ForeignKey("delivery_order.id"), nullable=False, comment="Заказ на доставку"
    )
    order: Mapped[int] = mapped_column(Integer, nullable=False, comment="Порядок")
    planned_time: Mapped[time | None] = mapped_column(Time, nullable=True, comment="Плановое время")
    actual_time: Mapped[time | None] = mapped_column(Time, nullable=True, comment="Фактическое время")
    status: Mapped[str] = mapped_column(String(20), default="pending", comment="Статус")

    route: Mapped["Route"] = relationship(back_populates="lines")
    delivery_order: Mapped["DeliveryOrder"] = relationship()
