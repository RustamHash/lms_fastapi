"""API для аутентификации."""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm

from app.api.deps import CurrentUser, Services
from app.api.v1.accounts.schemas import MeRead, RoleBrief, TokenResponse
from app.core.exceptions import NotFoundError, UnauthorizedError
from app.core.security import create_access_token

router = APIRouter(tags=["auth"])


@router.post("/auth/token", response_model=TokenResponse)
async def login(services: Services, form: Annotated[OAuth2PasswordRequestForm, Depends()]) -> TokenResponse:
    user = await services.user.authenticate(form.username, form.password)
    if user is None:
        raise UnauthorizedError("Неверное имя пользователя или пароль")
    token = create_access_token(user.id, user.username)
    return TokenResponse(access_token=token)


@router.post("/auth/register", include_in_schema=False)
async def register_removed() -> None:
    raise NotFoundError("Регистрация закрыта")


@router.get("/auth/me", response_model=MeRead)
async def me(user: CurrentUser, services: Services) -> MeRead:
    full = await services.user.get_by_id(user.id, with_depositors=True)
    if full is None:
        raise UnauthorizedError("Пользователь не найден или деактивирован")
    return MeRead(
        id=full.id,
        username=full.username,
        is_superuser=full.is_superuser,
        permissions=full.get_all_permissions(),
        roles=[
            RoleBrief.model_validate(role)
            for role in full.roles
            if not role.is_deleted
        ],
        depositor_ids=full.depositor_ids,
        client_ids=full.client_ids,
    )
