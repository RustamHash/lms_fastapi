"""Зависимости FastAPI."""

from __future__ import annotations

from collections.abc import AsyncGenerator

from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.accounts.repository import UserRepository
from app.core.database import async_session_factory
from app.core.security import decode_token_sub_user_id
from app.infrastructure.uow import UnitOfWork

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/token", auto_error=False)


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """Сессия с автоматическим commit/rollback."""
    async with UnitOfWork(async_session_factory) as session:
        yield session


async def get_current_user_id(
    token: str | None = Depends(oauth2_scheme),
) -> int | None:
    if not token:
        return None
    try:
        return decode_token_sub_user_id(token)
    except ValueError:
        return None


def require_permission(permission: str):
    """Зависимость — проверка права."""
    async def checker(
        session: AsyncSession = Depends(get_session),
        token: str | None = Depends(oauth2_scheme),
    ):
        from fastapi import HTTPException, status
        
        if not token:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Не авторизован")
        
        try:
            user_id = decode_token_sub_user_id(token)
        except ValueError:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Недействительный токен") from None
        
        repo = UserRepository(session)
        user = await repo.get_by_id(user_id)
        
        if user is None or not user.is_active:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Пользователь не найден")
        
        if not user.has_permission(permission):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=f"Нет права: {permission}")
        
        return user
    
    return checker


async def get_current_user(
    session: AsyncSession = Depends(get_session),
    token: str | None = Depends(oauth2_scheme),
):
    if not token:
        from fastapi import HTTPException, status
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Не авторизован",
        )
    try:
        user_id = decode_token_sub_user_id(token)
    except ValueError:
        from fastapi import HTTPException, status
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Недействительный токен",
        ) from None

    repo = UserRepository(session)
    user = await repo.get_by_id(user_id)
    if user is None or not user.is_active:
        from fastapi import HTTPException, status
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Пользователь не найден или деактивирован",
        )
    return user
