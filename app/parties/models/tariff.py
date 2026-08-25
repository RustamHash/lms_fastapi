"""Тарифы."""

from __future__ import annotations

from datetime import date
from decimal import Decimal

from sqlalchemy import Date, ForeignKey, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.infrastructure.orm_base import Base
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.parties.models.contract import Contract


class TariffDocument(Base):
    """Тарифный документ (приложение к договору)."""

    __tablename__ = "parties_tariff_document"

    contract_id: Mapped[int] = mapped_column(
        ForeignKey("parties_contract.id"), nullable=False, comment="Договор"
    )
    document_type: Mapped[str] = mapped_column(
        String(20), nullable=False, comment="Тип документа"
    )
    number: Mapped[str] = mapped_column(String(50), nullable=False, comment="Номер")
    date: Mapped[date] = mapped_column(Date, nullable=False, comment="Дата подписания")
    valid_from: Mapped[date] = mapped_column(
        Date, nullable=False, comment="Действует с"
    )
    valid_until: Mapped[date | None] = mapped_column(
        Date, nullable=True, comment="Действует до"
    )
    currency: Mapped[str] = mapped_column(String(3), default="RUB", comment="Валюта")
    vat_rate: Mapped[str] = mapped_column(
        String(10), default="20", comment="Ставка НДС"
    )
    file_id: Mapped[int | None] = mapped_column(
        ForeignKey("files.id"), nullable=True, comment="Скан документа"
    )

    contract: Mapped["Contract"] = relationship(
        back_populates="tariff_documents", lazy="selectin"
    )
    tariffs: Mapped[list["Tariff"]] = relationship(
        back_populates="document"
    )

    def __repr__(self) -> str:
        return f"<TariffDocument(id={self.id}, number={self.number})>"


class Tariff(Base):
    """Тариф."""

    __tablename__ = "parties_tariff"

    document_id: Mapped[int] = mapped_column(
        ForeignKey("parties_tariff_document.id"),
        nullable=False,
        comment="Тарифный документ",
    )
    service_group: Mapped[str] = mapped_column(
        String(20), nullable=False, comment="Группа услуг"
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False, comment="Название")
    description: Mapped[str] = mapped_column(Text, default="", comment="Описание")
    unit: Mapped[str] = mapped_column(
        String(20), nullable=False, comment="Единица измерения"
    )
    price: Mapped[Decimal] = mapped_column(
        Numeric(12, 2), nullable=False, comment="Цена"
    )

    document: Mapped["TariffDocument"] = relationship(
        back_populates="tariffs", lazy="selectin"
    )

    def __repr__(self) -> str:
        return f"<Tariff(id={self.id}, name={self.name}, price={self.price})>"
