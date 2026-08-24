"""API для управления правами пользователей."""

from __future__ import annotations

from fastapi import APIRouter, Depends

from app.accounts.repository import UserRepository
from app.api.deps import CurrentUser, Services, require_permission
from app.api.v1.accounts.schemas_permissions import (
    AvailablePermissionsRead,
    UserPermissionsRead,
    UserPermissionsUpdate,
)
from app.core.exceptions import ForbiddenError, NotFoundError

router = APIRouter(tags=["permissions"])

AVAILABLE_MODULES = [
    "users", "roles", "audit",
    "addresses", "legal_entities", "depositors", "clients", "contracts", "tariffs",
    "products", "batches", "lpns", "stock", "tasks",
    "documents", "delivery", "drivers", "vehicles", "routes",
    "notifications", "integrations", "files",
]

AVAILABLE_ACTIONS = ["view", "create", "update", "delete", "execute", "complete", "approve", "cancel"]


@router.get("/permissions/available", response_model=AvailablePermissionsRead, dependencies=[Depends(require_permission("view", "roles"))])
async def get_available_permissions() -> AvailablePermissionsRead:
    return AvailablePermissionsRead(modules=AVAILABLE_MODULES, actions=AVAILABLE_ACTIONS)


@router.get("/users/{user_id}/permissions", response_model=UserPermissionsRead, dependencies=[Depends(require_permission("view", "users"))])
async def get_user_permissions(user_id: int, services: Services) -> UserPermissionsRead:
    user = await UserRepository(services.session).get_by_id(user_id)
    if user is None:
        raise NotFoundError("Пользователь не найден")
    return UserPermissionsRead(
        user_id=user.id,
        permissions=user.get_all_permissions(),
        is_superuser=user.is_superuser,
        extra_permissions=user.extra_permissions or {},
    )


@router.put("/users/{user_id}/permissions", response_model=UserPermissionsRead, dependencies=[Depends(require_permission("update", "users"))])
async def update_user_permissions(user_id: int, body: UserPermissionsUpdate, services: Services, current_user: CurrentUser) -> UserPermissionsRead:
    user = await UserRepository(services.session).get_by_id(user_id)
    if user is None:
        raise NotFoundError("Пользователь не найден")

    if user.is_superuser and not current_user.is_superuser:
        raise ForbiddenError("Нельзя менять права суперпользователя")

    await UserRepository(services.session).update(user_id, extra_permissions=body.extra_permissions, updated_by_id=current_user.id)

    return UserPermissionsRead(
        user_id=user.id,
        permissions=user.get_all_permissions(),
        is_superuser=user.is_superuser,
        extra_permissions=user.extra_permissions or {},
    )
