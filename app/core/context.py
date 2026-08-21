"""Контекст текущего пользователя."""

from __future__ import annotations

from contextvars import ContextVar

# Текущий пользователь (user_id)
current_user_id: ContextVar[int | None] = ContextVar("current_user_id", default=None)


def set_current_user_id(user_id: int | None) -> None:
    """Установить текущего пользователя."""
    current_user_id.set(user_id)


def get_current_user_id_context() -> int | None:
    """Получить текущего пользователя."""
    return current_user_id.get()
