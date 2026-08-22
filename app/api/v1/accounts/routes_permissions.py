"""API для управления правами пользователей."""

from __future__ import annotations

from fastapi import HTTPException, APIRouter, Depends, status

from app.accounts.repository import UserRepository
from app.api.deps import CurrentUser, SessionDep, require_permission
from app.api.v1.accounts.schemas_permissions import (
    AvailablePermissionsRead,
    UserPermissionsRead,
    UserPermissionsUpdate,
)
from app.core.exceptions import NotFoundError

router = APIRouter(tags=["permissions"])

# Список всех модулей (entity)
AVAILABLE_MODULES = [
    "users",
    "roles",
    "audit",
    "addresses",
    "legal_entities",
    "depositors",
    "clients",
    "contracts",
    "tariffs",
    "products",
    "batches",
    "lpns",
    "stock",
    "tasks",
    "documents",
    "delivery",
    "drivers",
    "vehicles",
    "routes",
    "notifications",
    "integrations",
    "files",
]

# Список всех действий (action)
AVAILABLE_ACTIONS = [
    "view",
    "create",
    "update",
    "delete",
    "execute",
    "complete",
    "approve",
    "cancel",
]


@router.get(
    "/permissions/available",
    response_model=AvailablePermissionsRead,
    dependencies=[Depends(require_permission("view", "roles"))],
)
async def get_available_permissions() -> AvailablePermissionsRead:
    """Получить список всех доступных модулей и действий."""
    return AvailablePermissionsRead(
        modules=AVAILABLE_MODULES,
        actions=AVAILABLE_ACTIONS,
    )


@router.get(
    "/users/{user_id}/permissions",
    response_model=UserPermissionsRead,
    dependencies=[Depends(require_permission("view", "users"))],
)
async def get_user_permissions(
    user_id: int,
    session: SessionDep,
) -> UserPermissionsRead:
    """Получить права пользователя."""
    repo = UserRepository(session)
    user = await repo.get_by_id(user_id)
    if user is None:
        raise NotFoundError("Пользователь не найден")

    return UserPermissionsRead(
        user_id=user.id,
        permissions=user.get_all_permissions(),
        is_superuser=user.is_superuser,
        extra_permissions=user.extra_permissions or {},
    )


@router.put(
    "/users/{user_id}/permissions",
    response_model=UserPermissionsRead,
    dependencies=[Depends(require_permission("update", "users"))],
)
async def update_user_permissions(
    user_id: int,
    body: UserPermissionsUpdate,
    session: SessionDep,
    current_user: CurrentUser,
) -> UserPermissionsRead:
    """Обновить extra_permissions пользователя."""
    repo = UserRepository(session)
    user = await repo.get_by_id(user_id)
    if user is None:
        raise NotFoundError("Пользователь не найден")

    # Нельзя менять права суперпользователю
    if user.is_superuser and not current_user.is_superuser:
        from app.core.exceptions import ForbiddenError
        raise ForbiddenError("Нельзя менять права суперпользователя")

    # Обновляем extra_permissions
    user.extra_permissions = body.extra_permissions
    user.updated_by_id = current_user.id
    try:
        await session.flush()
    except Exception as e:
        await session.rollback()
        raise HTTPException(status_code=500, detail=f"Ошибка базы данных: {e}")

    return UserPermissionsRead(
        user_id=user.id,
        permissions=user.get_all_permissions(),
        is_superuser=user.is_superuser,
        extra_permissions=user.extra_permissions or {},
    )
