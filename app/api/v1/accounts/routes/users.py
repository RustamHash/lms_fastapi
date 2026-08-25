"""API для пользователей."""

from __future__ import annotations

from typing import NoReturn

from fastapi import APIRouter, Depends, status

from app.accounts.models import User
from app.api.deps import CurrentUser, Services, require_permission
from app.api.v1.accounts.schemas import (
    UserClientsUpdate,
    UserCreate,
    UserDepositorsUpdate,
    UserRead,
    UserRolesUpdate,
    UserUpdate,
)
from app.core.exceptions import BadRequestError, ConflictError, ForbiddenError, NotFoundError

router = APIRouter(tags=["users"])


def _guard_superuser(target: User, actor: User) -> None:
    if target.is_superuser and not actor.is_superuser:
        raise ForbiddenError("Нельзя менять роли или права суперпользователя")


def _map_user_write_error(exc: ValueError) -> NoReturn:
    message = str(exc)
    if "уже существует" in message:
        raise ConflictError(message) from exc
    raise BadRequestError(message) from exc


@router.get("/users", response_model=list[UserRead], dependencies=[Depends(require_permission("view", "users"))])
async def list_users(services: Services) -> list[UserRead]:
    users = await services.user.list_all()
    return [UserRead.model_validate(u) for u in users]


@router.post("/users", response_model=UserRead, status_code=status.HTTP_201_CREATED, dependencies=[Depends(require_permission("create", "users"))])
async def create_user(body: UserCreate, services: Services) -> UserRead:
    try:
        user = await services.user.create(
            username=body.username,
            password=body.password,
            phone=body.phone,
            email=body.email,
        )
    except ValueError as e:
        _map_user_write_error(e)
    return UserRead.model_validate(user)


@router.get("/users/{user_id}", response_model=UserRead, dependencies=[Depends(require_permission("view", "users"))])
async def get_user(user_id: int, services: Services) -> UserRead:
    user = await services.user.get_by_id(user_id, with_depositors=True)
    if user is None:
        raise NotFoundError("Пользователь не найден")
    return UserRead.model_validate(user)


@router.patch("/users/{user_id}", response_model=UserRead, dependencies=[Depends(require_permission("update", "users"))])
async def update_user(user_id: int, body: UserUpdate, services: Services) -> UserRead:
    user = await services.user.update(user_id, **body.model_dump(exclude_unset=True))
    if user is None:
        raise NotFoundError("Пользователь не найден")
    return UserRead.model_validate(user)


@router.delete("/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT, dependencies=[Depends(require_permission("delete", "users"))])
async def delete_user(user_id: int, services: Services, current_user: CurrentUser) -> None:
    user = await services.user.get_by_id(user_id, with_depositors=True)
    if user is None:
        raise NotFoundError("Пользователь не найден")
    if user.is_superuser and not current_user.is_superuser:
        raise ForbiddenError("Нельзя удалить суперпользователя")
    await services.user.soft_delete(user_id, current_user.id)


@router.get("/users/{user_id}/roles", response_model=UserRolesUpdate, dependencies=[Depends(require_permission("view", "users"))])
async def get_user_roles(user_id: int, services: Services) -> UserRolesUpdate:
    user = await services.user.get_by_id(user_id, with_depositors=True)
    if user is None:
        raise NotFoundError("Пользователь не найден")
    return UserRolesUpdate(
        role_ids=[role.id for role in user.roles if not role.is_deleted]
    )


@router.put("/users/{user_id}/roles", response_model=UserRead, dependencies=[Depends(require_permission("update", "users"))])
async def put_user_roles(
    user_id: int,
    body: UserRolesUpdate,
    services: Services,
    current_user: CurrentUser,
) -> UserRead:
    user = await services.user.get_by_id(user_id, with_depositors=True)
    if user is None:
        raise NotFoundError("Пользователь не найден")
    _guard_superuser(user, current_user)
    try:
        user = await services.user.set_roles(user_id, body.role_ids)
    except ValueError as e:
        _map_user_write_error(e)
    if user is None:
        raise NotFoundError("Пользователь не найден")
    return UserRead.model_validate(user)


@router.get("/users/{user_id}/depositors", response_model=UserDepositorsUpdate, dependencies=[Depends(require_permission("view", "users"))])
async def get_user_depositors(user_id: int, services: Services) -> UserDepositorsUpdate:
    user = await services.user.get_by_id(user_id, with_depositors=True)
    if user is None:
        raise NotFoundError("Пользователь не найден")
    return UserDepositorsUpdate(depositor_ids=user.depositor_ids)


@router.put("/users/{user_id}/depositors", response_model=UserRead, dependencies=[Depends(require_permission("update", "users"))])
async def put_user_depositors(
    user_id: int,
    body: UserDepositorsUpdate,
    services: Services,
    current_user: CurrentUser,
) -> UserRead:
    user = await services.user.get_by_id(user_id, with_depositors=True)
    if user is None:
        raise NotFoundError("Пользователь не найден")
    _guard_superuser(user, current_user)
    try:
        user = await services.user.set_depositors(user_id, body.depositor_ids)
    except ValueError as e:
        _map_user_write_error(e)
    if user is None:
        raise NotFoundError("Пользователь не найден")
    return UserRead.model_validate(user)


@router.get("/users/{user_id}/clients", response_model=UserClientsUpdate, dependencies=[Depends(require_permission("view", "users"))])
async def get_user_clients(user_id: int, services: Services) -> UserClientsUpdate:
    user = await services.user.get_by_id(user_id, with_depositors=True)
    if user is None:
        raise NotFoundError("Пользователь не найден")
    return UserClientsUpdate(client_ids=user.client_ids)


@router.put("/users/{user_id}/clients", response_model=UserRead, dependencies=[Depends(require_permission("update", "users"))])
async def put_user_clients(
    user_id: int,
    body: UserClientsUpdate,
    services: Services,
    current_user: CurrentUser,
) -> UserRead:
    user = await services.user.get_by_id(user_id, with_depositors=True)
    if user is None:
        raise NotFoundError("Пользователь не найден")
    _guard_superuser(user, current_user)
    try:
        user = await services.user.set_clients(user_id, body.client_ids)
    except ValueError as e:
        _map_user_write_error(e)
    if user is None:
        raise NotFoundError("Пользователь не найден")
    return UserRead.model_validate(user)
