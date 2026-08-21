"""API для модуля accounts."""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, status
from fastapi.security import OAuth2PasswordRequestForm

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
from app.api.deps import CurrentUser, SessionDep, UserDep, require_permission
from app.api.v1.accounts import schemas
from app.core.exceptions import ConflictError, NotFoundError, UnauthorizedError
from app.core.security import create_access_token

router = APIRouter(tags=["accounts"])


# ========== Auth ==========


@router.post("/auth/token", response_model=schemas.TokenResponse)
async def login(
    session: SessionDep,
    form: Annotated[OAuth2PasswordRequestForm, Depends()],
) -> schemas.TokenResponse:
    service = UserService(UserRepository(session))
    user = await service.authenticate(form.username, form.password)
    if user is None:
        raise UnauthorizedError("Неверное имя пользователя или пароль")
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
        raise ConflictError(str(e)) from e
    return schemas.UserRead.model_validate(user)


@router.get("/auth/me")
async def me(
    user: CurrentUser,
) -> dict:
    return {
        "id": user.id,
        "username": user.username,
        "phone": user.phone,
        "email": user.email,
        "is_superuser": user.is_superuser,
        "is_active": user.is_active,
        "permissions": user.get_all_permissions(),
    }


# ========== Users ==========


@router.get(
    "/users",
    response_model=list[schemas.UserRead],
    dependencies=[Depends(require_permission("view", "users"))],
)
async def list_users(session: SessionDep) -> list[schemas.UserRead]:
    service = UserService(UserRepository(session))
    users = await service.list_all()
    return [schemas.UserRead.model_validate(u) for u in users]


@router.get(
    "/users/{user_id}",
    response_model=schemas.UserRead,
    dependencies=[Depends(require_permission("view", "users"))],
)
async def get_user(user_id: int, session: SessionDep) -> schemas.UserRead:
    service = UserService(UserRepository(session))
    user = await service.get_by_id(user_id)
    if user is None:
        raise NotFoundError("Пользователь не найден")
    return schemas.UserRead.model_validate(user)


@router.patch(
    "/users/{user_id}",
    response_model=schemas.UserRead,
    dependencies=[Depends(require_permission("update", "users"))],
)
async def update_user(
    user_id: int,
    body: schemas.UserUpdate,
    session: SessionDep,
) -> schemas.UserRead:
    service = UserService(UserRepository(session))
    user = await service.update(user_id, **body.model_dump(exclude_unset=True))
    if user is None:
        raise NotFoundError("Пользователь не найден")
    return schemas.UserRead.model_validate(user)


# ========== Roles ==========


@router.get(
    "/roles",
    response_model=list[schemas.RoleRead],
    dependencies=[Depends(require_permission("view", "roles"))],
)
async def list_roles(session: SessionDep) -> list[schemas.RoleRead]:
    service = RoleService(RoleRepository(session))
    roles = await service.list_all()
    return [schemas.RoleRead.model_validate(r) for r in roles]


@router.get(
    "/roles/{role_id}",
    response_model=schemas.RoleRead,
    dependencies=[Depends(require_permission("view", "roles"))],
)
async def get_role(role_id: int, session: SessionDep) -> schemas.RoleRead:
    service = RoleService(RoleRepository(session))
    role = await service.get_by_id(role_id)
    if role is None:
        raise NotFoundError("Роль не найдена")
    return schemas.RoleRead.model_validate(role)


@router.post(
    "/roles",
    response_model=schemas.RoleRead,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_permission("create", "roles"))],
)
async def create_role(
    body: schemas.RoleCreate,
    session: SessionDep,
) -> schemas.RoleRead:
    service = RoleService(RoleRepository(session))
    try:
        role = await service.create(body.name, body.code, body.permissions)
    except ValueError as e:
        raise ConflictError(str(e)) from e
    return schemas.RoleRead.model_validate(role)


@router.delete(
    "/roles/{role_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(require_permission("delete", "roles"))],
)
async def delete_role(role_id: int, session: SessionDep, current_user: CurrentUser) -> None:
    from app.accounts.models import Role
    role = await session.get(Role, role_id)
    if role is None:
        raise NotFoundError("Роль не найдена")
    role.soft_delete(current_user.id)
    await session.flush()


@router.patch(
    "/roles/{role_id}/permissions",
    response_model=schemas.RoleRead,
    dependencies=[Depends(require_permission("update", "roles"))],
)
async def update_role_permissions(
    role_id: int,
    body: schemas.RolePermissionsUpdate,
    session: SessionDep,
) -> schemas.RoleRead:
    service = RoleService(RoleRepository(session))
    role = await service.update_permissions(role_id, body.permissions)
    if role is None:
        raise NotFoundError("Роль не найдена")
    return schemas.RoleRead.model_validate(role)


# ========== Audit ==========


@router.get(
    "/audit",
    response_model=list[schemas.AuditRead],
    dependencies=[Depends(require_permission("view", "audit"))],
)
async def list_audit(
    session: SessionDep,
    user_id: int | None = None,
) -> list[schemas.AuditRead]:
    service = AuditService(AuditRepository(session))
    if user_id:
        rows = await service.list_by_user(user_id)
    else:
        from app.accounts.models import Audit
        from sqlalchemy import select as sa_select
        rows = list(await session.scalars(
            sa_select(Audit).order_by(Audit.created_at.desc()).limit(100)
        ))
    return [schemas.AuditRead.model_validate(r) for r in rows]


@router.post(
    "/audit",
    response_model=schemas.AuditRead,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_permission("create", "audit"))],
)
async def create_audit(
    body: schemas.AuditCreate,
    session: SessionDep,
    user_id: UserDep,
) -> schemas.AuditRead:
    service = AuditService(AuditRepository(session))
    audit = await service.log(
        user_id=user_id,
        action=body.action,
        entity_type=body.entity_type,
        entity_id=body.entity_id,
        changes=body.changes,
    )
    return schemas.AuditRead.model_validate(audit)


@router.patch(
    "/audit/{audit_id}",
    response_model=schemas.AuditRead,
    dependencies=[Depends(require_permission("update", "audit"))],
)
async def update_audit(
    audit_id: int,
    body: schemas.AuditUpdate,
    session: SessionDep,
    user_id: UserDep,
) -> schemas.AuditRead:
    from app.accounts.models import Audit
    audit = await session.get(Audit, audit_id)
    if audit is None:
        raise NotFoundError("Запись аудита не найдена")
    for field, value in body.model_dump(exclude_unset=True).items():
        setattr(audit, field, value)
    audit.updated_by_id = user_id
    await session.flush()
    return schemas.AuditRead.model_validate(audit)


@router.delete(
    "/audit/{audit_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(require_permission("delete", "audit"))],
)
async def delete_audit(
    audit_id: int,
    session: SessionDep,
    user_id: UserDep,
) -> None:
    from app.accounts.models import Audit
    audit = await session.get(Audit, audit_id)
    if audit is None:
        raise NotFoundError("Запись аудита не найдена")
    audit.soft_delete(user_id)
    await session.flush()


@router.get(
    "/audit/{audit_id}",
    response_model=schemas.AuditRead,
    dependencies=[Depends(require_permission("view", "audit"))],
)
async def get_audit(
    audit_id: int,
    session: SessionDep,
) -> schemas.AuditRead:
    from app.accounts.models import Audit

    audit = await session.get(Audit, audit_id)
    if audit is None:
        raise NotFoundError("Запись аудита не найдена")
    return schemas.AuditRead.model_validate(audit)
