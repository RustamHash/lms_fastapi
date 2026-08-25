"""Расхождения приёмки."""

from __future__ import annotations

from decimal import Decimal

from sqlalchemy import ForeignKey, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.infrastructure.orm_base import Base


class ReceivingDiscrepancy(Base):
    """План/факт по строке приёмки."""

    __tablename__ = "warehouse_receiving_discrepancy"

    task_line_id: Mapped[int] = mapped_column(
        ForeignKey("warehouse_task_line.id"), nullable=False, comment="Строка задания"
    )
    discrepancy_type: Mapped[str] = mapped_column(
        String(20), nullable=False, comment="shortage / surplus"
    )
    qty_planned: Mapped[Decimal] = mapped_column(Numeric(20, 3), nullable=False, comment="План")
    qty_fact: Mapped[Decimal] = mapped_column(Numeric(20, 3), nullable=False, comment="Факт")
    status: Mapped[str] = mapped_column(String(20), default="detected", comment="Статус")

    task_line: Mapped["TaskLine"] = relationship()
