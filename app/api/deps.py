"""Общие зависимости для API."""

from __future__ import annotations

from typing import Annotated

from fastapi import Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.accounts.models import User
from app.core.dependencies import get_current_user, get_current_user_id, get_session
from app.core.exceptions import ForbiddenError

# ========== Базовые зависимости ==========

# Сессия БД с автоматическим commit/rollback
SessionDep = Annotated[AsyncSession, Depends(get_session)]

# ID текущего пользователя (None, если не авторизован)
UserDep = Annotated[int | None, Depends(get_current_user_id)]

# Текущий пользователь (объект User, требует авторизации)
CurrentUser = Annotated[User, Depends(get_current_user)]


# ========== Пагинация ==========

class PaginationParams:
    """Параметры пагинации для list-роутов."""

    def __init__(
        self,
        limit: int = Query(50, ge=1, le=500, description="Количество записей"),
        offset: int = Query(0, ge=0, description="Смещение"),
    ) -> None:
        self.limit = limit
        self.offset = offset


# ========== Проверка прав ==========

def require_permission(action: str, entity: str):
    """
    Проверка конкретного права.

    Args:
        action: Действие (view, create, update, delete, approve, execute, complete)
        entity: Модуль (products, documents, delivery, users, ...)

    Returns:
        Зависимость FastAPI для проверки права
    """
    async def checker(current_user: CurrentUser) -> User:
        if not current_user.has_permission(action, entity):
            raise ForbiddenError(f"Нет права: {action}:{entity}")
        return current_user

    return checker


def require_group(entity: str):
    """
    Проверка доступа к модулю (группе).

    Args:
        entity: Модуль (products, documents, delivery, ...)

    Returns:
        Зависимость FastAPI для проверки доступа к модулю
    """
    async def checker(current_user: CurrentUser) -> User:
        if not current_user.has_group_access(entity):
            raise ForbiddenError(f"Нет доступа к модулю: {entity}")
        return current_user

    return checker
