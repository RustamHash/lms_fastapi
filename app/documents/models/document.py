"""Документы."""

from __future__ import annotations

from datetime import date
from decimal import Decimal

from sqlalchemy import Boolean, Date, ForeignKey, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.infrastructure.orm_base import Base
from app.core.statuses import DocumentStatus


class Document(Base):
    """Складской документ."""

    __tablename__ = "documents_document"

    document_number: Mapped[str] = mapped_column(String(50), nullable=False, comment="Номер документа")
    document_date: Mapped[date | None] = mapped_column(Date, nullable=True, comment="Дата документа")
    delivery_date: Mapped[date | None] = mapped_column(Date, nullable=True, comment="Дата доставки")
    document_type: Mapped[str] = mapped_column(String(20), nullable=False, comment="Тип документа")
    contract_id: Mapped[int | None] = mapped_column(
        ForeignKey("parties_contract.id"), nullable=True, comment="Договор"
    )
    warehouse_id: Mapped[int] = mapped_column(
        ForeignKey("warehouse_warehouse.id"), nullable=False, comment="Склад"
    )
    virtual_warehouse_id: Mapped[int | None] = mapped_column(
        ForeignKey("warehouse_virtual_warehouse.id"), nullable=True, comment="Виртуальный склад"
    )
    status: Mapped[str] = mapped_column(String(20), default=DocumentStatus.DRAFT.value, comment="Статус")
    is_delivery: Mapped[bool] = mapped_column(Boolean, default=False, comment="Признак доставки")
    is_edo: Mapped[bool] = mapped_column(Boolean, default=False, comment="Признак ЭДО")

    lines: Mapped[list["DocumentLine"]] = relationship(back_populates="document", cascade="all, delete-orphan")


class DocumentLine(Base):
    """Строка документа."""

    __tablename__ = "documents_document_line"

    document_id: Mapped[int] = mapped_column(
        ForeignKey("documents_document.id"), nullable=False, comment="Документ"
    )
    product_id: Mapped[int] = mapped_column(
        ForeignKey("warehouse_product.id"), nullable=False, comment="Товар"
    )
    batch_id: Mapped[int | None] = mapped_column(
        ForeignKey("warehouse_batch.id"), nullable=True, comment="Партия"
    )
    quantity: Mapped[Decimal] = mapped_column(Numeric(20, 3), nullable=False, comment="Количество")
    processed_quantity: Mapped[Decimal] = mapped_column(
        Numeric(20, 3), default=Decimal("0"), comment="Обработано"
    )

    document: Mapped["Document"] = relationship(back_populates="lines")
    product: Mapped["Product"] = relationship()
    batch: Mapped["Batch | None"] = relationship()
