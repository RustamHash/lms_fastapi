"""Клиент."""

from __future__ import annotations

from sqlalchemy import Boolean, ForeignKey, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.infrastructure.orm_base import Base
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.parties.models.address import Address
    from app.parties.models.counterparty import Depositor


class Client(Base):
    """Клиент поклажедателя (код + адрес доставки)."""

    __tablename__ = "parties_client"
    __table_args__ = (
        UniqueConstraint(
            "depositor_id",
            "code",
            "delivery_address_id",
            name="uq_client_depositor_code_address",
        ),
    )

    depositor_id: Mapped[int] = mapped_column(
        ForeignKey("parties_depositor.id"), nullable=False, comment="Поклажедатель"
    )
    code: Mapped[str] = mapped_column(String(50), nullable=False, comment="Код клиента")
    name: Mapped[str] = mapped_column(
        String(255), nullable=False, comment="Наименование"
    )
    legal_name: Mapped[str] = mapped_column(
        String(255), default="", comment="Полное наименование"
    )
    inn: Mapped[str] = mapped_column(String(12), default="", comment="ИНН")
    kpp: Mapped[str] = mapped_column(String(9), default="", comment="КПП")
    legal_address_id: Mapped[int | None] = mapped_column(
        ForeignKey("parties_address.id"), nullable=True, comment="Юридический адрес"
    )
    delivery_address_id: Mapped[int | None] = mapped_column(
        ForeignKey("parties_address.id"), nullable=True, comment="Адрес доставки"
    )
    is_edo: Mapped[bool] = mapped_column(Boolean, default=False, comment="Признак ЭДО")

    depositor: Mapped["Depositor"] = relationship()
    legal_address: Mapped["Address | None"] = relationship(
        foreign_keys=[legal_address_id]
    )
    delivery_address: Mapped["Address | None"] = relationship(
        foreign_keys=[delivery_address_id]
    )

    def __repr__(self) -> str:
        return f"<Client(id={self.id}, code={self.code})>"
