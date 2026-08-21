"""Общие зависимости для API."""

from __future__ import annotations

from typing import Annotated

from fastapi import Depends, HTTPException, Query, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.accounts.models import User
from app.accounts.repository import UserRepository
from app.core.database import async_session_factory
from app.core.exceptions import ForbiddenError
from app.core.security import decode_token_sub_user_id
from app.infrastructure.uow import UnitOfWork

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/token", auto_error=False)


# ========== Базовые зависимости ==========

async def get_session():
    """Сессия с автоматическим commit/rollback."""
    async with UnitOfWork(async_session_factory) as session:
        yield session


async def get_current_user_id(
    token: str | None = Depends(oauth2_scheme),
) -> int | None:
    """ID текущего пользователя (None, если не авторизован)."""
    if not token:
        return None
    try:
        return decode_token_sub_user_id(token)
    except ValueError:
        return None


async def get_current_user(
    session: AsyncSession = Depends(get_session),
    token: str | None = Depends(oauth2_scheme),
) -> User:
    """Текущий пользователь (объект User, требует авторизации)."""
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Не авторизован",
        )
    try:
        user_id = decode_token_sub_user_id(token)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Недействительный токен",
        ) from None

    repo = UserRepository(session)
    user = await repo.get_by_id(user_id)
    if user is None or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Пользователь не найден или деактивирован",
        )
    return user


# ========== Аннотированные зависимости ==========

SessionDep = Annotated[AsyncSession, Depends(get_session)]
UserDep = Annotated[int | None, Depends(get_current_user_id)]
CurrentUser = Annotated[User, Depends(get_current_user)]


# ========== Пагинация ==========

class PaginationParams:
    """Параметры пагинации для list-роутов."""

    def __init__(
        self,
        limit: int = Query(1000, ge=1, le=5000, description="Количество записей"),
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
