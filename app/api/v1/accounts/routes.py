"""API для модуля accounts."""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from app.accounts.repository import (
    AuditRepository,
    RoleRepository,
    UserRepository,
    UserSettingsRepository,
    UserTableSettingsRepository,
)
from app.accounts.services import (
    AuditService,
    RoleService,
    TableSettingsService,
    UserService,
)
from app.api.v1.accounts import schemas
from app.core.dependencies import get_current_user, get_current_user_id, get_session
from app.core.security import create_access_token

router = APIRouter(tags=["accounts"])

SessionDep = Annotated[AsyncSession, Depends(get_session)]
UserDep = Annotated[int | None, Depends(get_current_user_id)]


# ========== Auth ==========


@router.post("/auth/token", response_model=schemas.TokenResponse)
async def login(
    session: SessionDep,
    form: Annotated[OAuth2PasswordRequestForm, Depends()],
) -> schemas.TokenResponse:
    service = UserService(UserRepository(session))
    user = await service.authenticate(form.username, form.password)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неверное имя пользователя или пароль",
        )
    token = create_access_token(user.id, user.username)
    return schemas.TokenResponse(access_token=token)


@router.post(
    "/auth/register",
    response_model=schemas.UserRead,
    status_code=status.HTTP_201_CREATED,
)
async def register(
    body: schemas.UserCreate,
    session: SessionDep,
) -> schemas.UserRead:
    service = UserService(UserRepository(session))
    try:
        user = await service.create(
            username=body.username,
            password=body.password,
            phone=body.phone,
            email=body.email,
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e)) from e
    return schemas.UserRead.model_validate(user)


@router.get("/auth/me")
async def me(
    user: Annotated[object, Depends(get_current_user)],
) -> dict:
    return {
        "id": user.id,
        "username": user.username,
        "phone": user.phone,
        "email": user.email,
        "is_superuser": user.is_superuser,
        "is_active": user.is_active,
        "permissions": user.get_permissions(),
    }


# ========== Users ==========


@router.get("/users", response_model=list[schemas.UserRead])
async def list_users(session: SessionDep) -> list[schemas.UserRead]:
    service = UserService(UserRepository(session))
    users = await service.list_all()
    return [schemas.UserRead.model_validate(u) for u in users]


@router.get("/users/{user_id}", response_model=schemas.UserRead)
async def get_user(user_id: int, session: SessionDep) -> schemas.UserRead:
    service = UserService(UserRepository(session))
    user = await service.get_by_id(user_id)
    if user is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Пользователь не найден")
    return schemas.UserRead.model_validate(user)


@router.patch("/users/{user_id}", response_model=schemas.UserRead)
async def update_user(
    user_id: int,
    body: schemas.UserUpdate,
    session: SessionDep,
) -> schemas.UserRead:
    service = UserService(UserRepository(session))
    user = await service.update(user_id, **body.model_dump(exclude_unset=True))
    if user is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Пользователь не найден")
    return schemas.UserRead.model_validate(user)


# ========== Roles ==========


@router.get("/roles", response_model=list[schemas.RoleRead])
async def list_roles(session: SessionDep) -> list[schemas.RoleRead]:
    service = RoleService(RoleRepository(session))
    roles = await service.list_all()
    return [schemas.RoleRead.model_validate(r) for r in roles]


@router.post(
    "/roles", response_model=schemas.RoleRead, status_code=status.HTTP_201_CREATED
)
async def create_role(
    body: schemas.RoleCreate,
    session: SessionDep,
) -> schemas.RoleRead:
    service = RoleService(RoleRepository(session))
    try:
        role = await service.create(body.name, body.code, body.permissions)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e)) from e
    return schemas.RoleRead.model_validate(role)


# ========== Audit ==========


@router.get("/audit", response_model=list[schemas.AuditRead])
async def list_audit(
    session: SessionDep,
    user_id: int | None = None,
) -> list[schemas.AuditRead]:
    service = AuditService(AuditRepository(session))
    if user_id:
        rows = await service.list_by_user(user_id)
    else:
        rows = []
    return [schemas.AuditRead.model_validate(r) for r in rows]


# ========== Table Settings ==========


@router.get("/table-settings/{table_id}", response_model=schemas.TableSettingsRead)
async def get_table_settings(
    table_id: str,
    session: SessionDep,
    user_id: UserDep,
) -> schemas.TableSettingsRead:
    if user_id is None:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, detail="Не авторизован")
    service = TableSettingsService(UserTableSettingsRepository(session))
    settings = await service.get_or_create(user_id, table_id)
    return schemas.TableSettingsRead(
        prefs=schemas.TableSettingsData(
            order=settings.columns_order,
            hidden=settings.hidden_columns,
            widths=settings.column_widths,
        )
    )


@router.put("/table-settings/{table_id}", response_model=schemas.TableSettingsRead)
async def update_table_settings(
    table_id: str,
    body: schemas.TableSettingsUpdate,
    session: SessionDep,
    user_id: UserDep,
) -> schemas.TableSettingsRead:
    if user_id is None:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, detail="Не авторизован")
    service = TableSettingsService(UserTableSettingsRepository(session))
    settings = await service.update(
        user_id,
        table_id,
        columns_order=body.order,
        hidden_columns=body.hidden,
        column_widths=body.widths,
    )
    if settings is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Настройки не найдены")
    return schemas.TableSettingsRead(
        prefs=schemas.TableSettingsData(
            order=settings.columns_order,
            hidden=settings.hidden_columns,
            widths=settings.column_widths,
        )
    )
