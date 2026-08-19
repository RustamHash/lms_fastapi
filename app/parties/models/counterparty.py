"""Поклажедатель, хранитель, перевозчик."""

from __future__ import annotations

from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.infrastructure.orm_base import Base


class Depositor(Base):
    """Поклажедатель."""

    __tablename__ = "parties_depositor"

    legal_entity_id: Mapped[int] = mapped_column(
        ForeignKey("parties_legal_entity.id"),
        unique=True,
        nullable=False,
        comment="Юрлицо",
    )
    code: Mapped[str] = mapped_column(
        String(50), default="", comment="Код поклажедателя"
    )

    def __repr__(self) -> str:
        return f"<Depositor(id={self.id}, code={self.code})>"


class Keeper(Base):
    """Хранитель."""

    __tablename__ = "parties_keeper"

    legal_entity_id: Mapped[int] = mapped_column(
        ForeignKey("parties_legal_entity.id"),
        unique=True,
        nullable=False,
        comment="Юрлицо",
    )

    def __repr__(self) -> str:
        return f"<Keeper(id={self.id})>"


class Carrier(Base):
    """Перевозчик."""

    __tablename__ = "parties_carrier"

    legal_entity_id: Mapped[int] = mapped_column(
        ForeignKey("parties_legal_entity.id"),
        unique=True,
        nullable=False,
        comment="Юрлицо",
    )

    def __repr__(self) -> str:
        return f"<Carrier(id={self.id})>"
