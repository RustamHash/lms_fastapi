"""Модель роли."""

from __future__ import annotations

from typing import Any

from sqlalchemy import Column, ForeignKey, String, Table
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.infrastructure.orm_base import Base

# Связующая таблица многие-ко-многим
user_roles = Table(
    "accounts_user_roles",
    Base.metadata,
    Column("user_id", ForeignKey("accounts_user.id"), primary_key=True),
    Column("role_id", ForeignKey("accounts_role.id"), primary_key=True),
)


class Role(Base):
    """Роль пользователя."""

    __tablename__ = "accounts_role"

    name: Mapped[str] = mapped_column(String(100), unique=True, comment="Название")
    code: Mapped[str] = mapped_column(String(50), unique=True, comment="Код")
    permissions: Mapped[dict[str, Any]] = mapped_column(
        JSONB, default=dict, comment="Права"
    )
    parent_role_id: Mapped[int | None] = mapped_column(
        ForeignKey("accounts_role.id"), nullable=True, comment="Родительская роль"
    )

    users: Mapped[list["User"]] = relationship(
        secondary=user_roles,
        back_populates="roles",
    )
    parent_role: Mapped["Role | None"] = relationship(
        remote_side="Role.id",
        back_populates="child_roles",
    )
    child_roles: Mapped[list["Role"]] = relationship(
        back_populates="parent_role",
    )
