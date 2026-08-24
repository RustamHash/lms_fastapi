"""API для аутентификации."""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm

from app.accounts.repository import UserRepository
from app.accounts.services import UserService
from app.api.deps import CurrentUser, Services
from app.api.v1.accounts.schemas import TokenResponse, UserCreate, UserRead
from app.core.exceptions import ConflictError, UnauthorizedError
from app.core.security import create_access_token

router = APIRouter(tags=["auth"])


@router.post("/auth/token", response_model=TokenResponse)
async def login(services: Services, form: Annotated[OAuth2PasswordRequestForm, Depends()]) -> TokenResponse:
    service = UserService(UserRepository(services.session))
    user = await service.authenticate(form.username, form.password)
    if user is None:
        raise UnauthorizedError("Неверное имя пользователя или пароль")
    token = create_access_token(user.id, user.username)
    return TokenResponse(access_token=token)


@router.post("/auth/register", response_model=UserRead, status_code=201)
async def register(body: UserCreate, services: Services) -> UserRead:
    service = UserService(UserRepository(services.session))
    try:
        user = await service.create(username=body.username, password=body.password, phone=body.phone, email=body.email)
    except ValueError as e:
        raise ConflictError(str(e)) from e
    return UserRead.model_validate(user)


@router.get("/auth/me")
async def me(user: CurrentUser) -> dict:
    return {
        "id": user.id,
        "username": user.username,
        "phone": user.phone,
        "email": user.email,
        "is_superuser": user.is_superuser,
        "is_active": user.is_active,
        "permissions": user.get_all_permissions(),
    }
