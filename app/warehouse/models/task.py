"""Задания."""

from __future__ import annotations

from decimal import Decimal

from sqlalchemy import Boolean, ForeignKey, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.infrastructure.orm_base import Base
from app.core.statuses import TaskStatus


class Task(Base):
    """Задание."""

    __tablename__ = "warehouse_task"

    task_type: Mapped[str] = mapped_column(String(20), nullable=False, comment="Тип задания")
    document_id: Mapped[int | None] = mapped_column(
        ForeignKey("documents_document.id"), nullable=True, comment="Документ"
    )
    inbound_order_id: Mapped[int | None] = mapped_column(
        ForeignKey("orders_inbound.id"), nullable=True, comment="Входящий заказ"
    )
    outbound_order_id: Mapped[int | None] = mapped_column(
        ForeignKey("orders_outbound.id"), nullable=True, comment="Исходящий заказ"
    )
    assignee_id: Mapped[int | None] = mapped_column(
        ForeignKey("accounts_user.id"), nullable=True, comment="Исполнитель"
    )
    status: Mapped[str] = mapped_column(String(30), default=TaskStatus.NEW.value, comment="Статус")

    lines: Mapped[list["TaskLine"]] = relationship(back_populates="task", cascade="all, delete-orphan")


class TaskLine(Base):
    """Строка задания."""

    __tablename__ = "warehouse_task_line"

    task_id: Mapped[int] = mapped_column(
        ForeignKey("warehouse_task.id"), nullable=False, comment="Задание"
    )
    product_id: Mapped[int] = mapped_column(
        ForeignKey("warehouse_product.id"), nullable=False, comment="Товар"
    )
    document_line_id: Mapped[int | None] = mapped_column(
        ForeignKey("documents_document_line.id"), nullable=True, comment="Строка документа"
    )
    inbound_order_line_id: Mapped[int | None] = mapped_column(
        ForeignKey("orders_inbound_line.id"), nullable=True, comment="Строка входящего заказа"
    )
    outbound_order_line_id: Mapped[int | None] = mapped_column(
        ForeignKey("orders_outbound_line.id"), nullable=True, comment="Строка исходящего заказа"
    )
    plan_qty: Mapped[Decimal] = mapped_column(
        Numeric(20, 3), default=Decimal("0"), comment="План"
    )
    fact_qty: Mapped[Decimal] = mapped_column(
        Numeric(20, 3), default=Decimal("0"), comment="Факт"
    )
    from_location_id: Mapped[int | None] = mapped_column(
        ForeignKey("warehouse_location.id"), nullable=True, comment="Откуда"
    )
    to_location_id: Mapped[int | None] = mapped_column(
        ForeignKey("warehouse_location.id"), nullable=True, comment="Куда"
    )
    lpn_id: Mapped[int | None] = mapped_column(
        ForeignKey("warehouse_lpn.id"), nullable=True, comment="LPN"
    )
    batch_id: Mapped[int | None] = mapped_column(
        ForeignKey("warehouse_batch.id"), nullable=True, comment="Партия"
    )
    reserved: Mapped[bool] = mapped_column(
        Boolean, default=False, nullable=False, comment="Резерв на остатке"
    )

    task: Mapped["Task"] = relationship(back_populates="lines")
    product: Mapped["Product"] = relationship()
    from_location: Mapped["Location | None"] = relationship(foreign_keys=[from_location_id])
    to_location: Mapped["Location | None"] = relationship(foreign_keys=[to_location_id])
    lpn: Mapped["LPN | None"] = relationship()
    batch: Mapped["Batch | None"] = relationship()
