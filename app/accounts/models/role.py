"""Модель роли."""

from __future__ import annotations

from sqlalchemy import Column, ForeignKey, Index, String, Table, text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import TYPE_CHECKING

from app.infrastructure.orm_base import Base

if TYPE_CHECKING:
    from app.accounts.models.user import User

user_roles = Table(
    "accounts_user_roles",
    Base.metadata,
    Column(
        "user_id",
        ForeignKey("accounts_user.id", ondelete="CASCADE"),
        primary_key=True,
    ),
    Column(
        "role_id",
        ForeignKey("accounts_role.id", ondelete="CASCADE"),
        primary_key=True,
    ),
)


class Role(Base):
    """Роль пользователя."""

    __tablename__ = "accounts_role"
    __table_args__ = (
        Index(
            "uq_accounts_role_code_alive",
            "code",
            unique=True,
            postgresql_where=text("is_deleted = false"),
        ),
        Index(
            "uq_accounts_role_name_alive",
            "name",
            unique=True,
            postgresql_where=text("is_deleted = false"),
        ),
    )

    name: Mapped[str] = mapped_column(String(100), comment="Название")
    code: Mapped[str] = mapped_column(String(50), comment="Код")
    permissions: Mapped[dict[str, list[str]]] = mapped_column(
        JSONB, default=dict, comment="Права"
    )

    users: Mapped[list["User"]] = relationship(
        secondary=user_roles,
        back_populates="roles",
    )
