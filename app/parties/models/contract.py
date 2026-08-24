"""Договор."""

from __future__ import annotations

from datetime import date
from typing import Any

from sqlalchemy import Date, ForeignKey, JSON, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.infrastructure.orm_base import Base

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.parties.models.legal_entity import LegalEntity
    from app.parties.models.tariff import TariffDocument


class Contract(Base):
    """Договор между юрлицами."""

    __tablename__ = "parties_contract"

    number: Mapped[str] = mapped_column(
        String(50), nullable=False, comment="Номер договора"
    )
    customer_id: Mapped[int] = mapped_column(
        ForeignKey("parties_legal_entity.id"), nullable=False, comment="Заказчик"
    )
    executor_id: Mapped[int] = mapped_column(
        ForeignKey("parties_legal_entity.id"), nullable=False, comment="Исполнитель"
    )
    contract_type: Mapped[str] = mapped_column(
        String(20), nullable=False, comment="Тип договора"
    )
    start_date: Mapped[date] = mapped_column(
        Date, nullable=False, comment="Дата начала"
    )
    end_date: Mapped[date | None] = mapped_column(
        Date, nullable=True, comment="Дата окончания"
    )
    status: Mapped[str] = mapped_column(String(20), default="active", comment="Статус")
    terms: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict, comment="Условия")

    customer: Mapped["LegalEntity"] = relationship(
        foreign_keys=[customer_id], lazy="selectin"
    )
    executor: Mapped["LegalEntity"] = relationship(
        foreign_keys=[executor_id], lazy="selectin"
    )
    tariff_documents: Mapped[list["TariffDocument"]] = relationship(
        back_populates="contract", lazy="selectin"
    )

    def __repr__(self) -> str:
        return f"<Contract(id={self.id}, number={self.number})>"
