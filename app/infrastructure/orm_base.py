"""Базовый класс для всех ORM-моделей."""

from __future__ import annotations

from datetime import UTC, datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    """Базовый класс с audit-полями и soft delete."""

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True, comment="ID записи")
    is_active: Mapped[bool] = mapped_column(
        Boolean, nullable=False, server_default="true", comment="Активна"
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False, comment="Создана"
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
        comment="Обновлена",
    )
    created_by_id: Mapped[int | None] = mapped_column(
        ForeignKey("accounts_user.id"), nullable=True, comment="Создал (user ID)"
    )
    updated_by_id: Mapped[int | None] = mapped_column(
        ForeignKey("accounts_user.id"), nullable=True, comment="Изменил (user ID)"
    )
    is_deleted: Mapped[bool] = mapped_column(
        Boolean, nullable=False, server_default="false", comment="Удалена (soft)"
    )
    deleted_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True, comment="Удалена (когда)"
    )
    deleted_by_id: Mapped[int | None] = mapped_column(
        ForeignKey("accounts_user.id"), nullable=True, comment="Удалил (user ID)"
    )

    def activate(self, user_id: int | None = None) -> None:
        self.is_active = True
        self.updated_by_id = user_id

    def deactivate(self, user_id: int | None = None) -> None:
        self.is_active = False
        self.updated_by_id = user_id

    def soft_delete(self, user_id: int | None = None) -> None:
        self.is_deleted = True
        self.is_active = False
        self.deleted_at = datetime.now(UTC)
        self.deleted_by_id = user_id

    def restore(self, user_id: int | None = None) -> None:
        self.is_deleted = False
        self.is_active = True
        self.deleted_at = None
        self.deleted_by_id = None
        self.updated_by_id = user_id

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__}(id={self.id})>"
