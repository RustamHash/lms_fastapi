"""Клиент и торговая точка."""

from __future__ import annotations

from sqlalchemy import Boolean, ForeignKey, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.infrastructure.orm_base import Base


class Client(Base):
    """Клиент поклажедателя."""

    __tablename__ = "parties_client"
    __table_args__ = (
        UniqueConstraint("depositor_id", "external_id", name="uq_client_depositor_external"),
    )

    depositor_id: Mapped[int] = mapped_column(
        ForeignKey("parties_depositor.id"), nullable=False, comment="Поклажедатель"
    )
    external_id: Mapped[str] = mapped_column(
        String(50), nullable=False, comment="Внешний код"
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False, comment="Наименование")
    legal_name: Mapped[str] = mapped_column(
        String(255), default="", comment="Полное наименование"
    )
    inn: Mapped[str] = mapped_column(String(12), default="", comment="ИНН")
    kpp: Mapped[str] = mapped_column(String(9), default="", comment="КПП")
    legal_address_id: Mapped[int | None] = mapped_column(
        ForeignKey("parties_address.id"), nullable=True, comment="Юридический адрес"
    )
    is_edo: Mapped[bool] = mapped_column(Boolean, default=False, comment="Признак ЭДО")

    depositor: Mapped["Depositor"] = relationship()
    legal_address: Mapped["Address | None"] = relationship(foreign_keys=[legal_address_id])
    trade_points: Mapped[list["TradePoint"]] = relationship(back_populates="client")

    def __repr__(self) -> str:
        return f"<Client(id={self.id}, name={self.name})>"


class TradePoint(Base):
    """Торговая точка клиента."""

    __tablename__ = "parties_trade_point"
    __table_args__ = (
        UniqueConstraint("client_id", "address_id", name="uq_trade_point_client_address"),
    )

    client_id: Mapped[int] = mapped_column(
        ForeignKey("parties_client.id"), nullable=False, comment="Клиент"
    )
    address_id: Mapped[int] = mapped_column(
        ForeignKey("parties_address.id"), nullable=False, comment="Адрес"
    )
    name: Mapped[str] = mapped_column(String(255), default="", comment="Название")

    client: Mapped["Client"] = relationship(back_populates="trade_points")
    address: Mapped["Address"] = relationship(back_populates="trade_points")

    def __repr__(self) -> str:
        return f"<TradePoint(id={self.id}, name={self.name})>"
