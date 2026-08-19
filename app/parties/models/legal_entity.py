"""Юридическое лицо."""

from __future__ import annotations

from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.infrastructure.orm_base import Base


class LegalEntity(Base):
    """Юридическое лицо."""

    __tablename__ = "parties_legal_entity"

    name: Mapped[str] = mapped_column(
        String(255), nullable=False, comment="Краткое наименование"
    )
    legal_name: Mapped[str] = mapped_column(
        String(255), default="", comment="Полное наименование"
    )
    inn: Mapped[str] = mapped_column(String(12), default="", comment="ИНН")
    kpp: Mapped[str] = mapped_column(String(9), default="", comment="КПП")
    ogrn: Mapped[str] = mapped_column(String(15), default="", comment="ОГРН")
    legal_address_id: Mapped[int | None] = mapped_column(
        ForeignKey("parties_address.id"), nullable=True, comment="Юридический адрес"
    )
    actual_address_id: Mapped[int | None] = mapped_column(
        ForeignKey("parties_address.id"), nullable=True, comment="Фактический адрес"
    )
    phone: Mapped[str] = mapped_column(String(20), default="", comment="Телефон")
    email: Mapped[str] = mapped_column(String(255), default="", comment="Email")
    edo_uuid: Mapped[str | None] = mapped_column(
        String(36), nullable=True, comment="Идентификатор ЭДО"
    )

    def __repr__(self) -> str:
        return f"<LegalEntity(id={self.id}, name={self.name})>"
