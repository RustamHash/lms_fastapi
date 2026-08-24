"""API для пользователей."""

from __future__ import annotations

from fastapi import APIRouter, Depends, status

from app.accounts.repository import UserRepository
from app.accounts.services import UserService
from app.api.deps import CurrentUser, Services, require_permission
from app.api.v1.accounts.schemas import UserCreate, UserRead, UserUpdate
from app.core.exceptions import ConflictError, ForbiddenError, NotFoundError

router = APIRouter(tags=["users"])


@router.get("/users", response_model=list[UserRead], dependencies=[Depends(require_permission("view", "users"))])
async def list_users(services: Services) -> list[UserRead]:
    service = UserService(UserRepository(services.session))
    users = await service.list_all()
    return [UserRead.model_validate(u) for u in users]


@router.post("/users", response_model=UserRead, status_code=status.HTTP_201_CREATED, dependencies=[Depends(require_permission("create", "users"))])
async def create_user(body: UserCreate, services: Services) -> UserRead:
    service = UserService(UserRepository(services.session))
    try:
        user = await service.create(username=body.username, password=body.password, phone=body.phone, email=body.email)
    except ValueError as e:
        raise ConflictError(str(e)) from e
    return UserRead.model_validate(user)


@router.get("/users/{user_id}", response_model=UserRead, dependencies=[Depends(require_permission("view", "users"))])
async def get_user(user_id: int, services: Services) -> UserRead:
    service = UserService(UserRepository(services.session))
    user = await service.get_by_id(user_id)
    if user is None:
        raise NotFoundError("Пользователь не найден")
    return UserRead.model_validate(user)


@router.patch("/users/{user_id}", response_model=UserRead, dependencies=[Depends(require_permission("update", "users"))])
async def update_user(user_id: int, body: UserUpdate, services: Services) -> UserRead:
    service = UserService(UserRepository(services.session))
    user = await service.update(user_id, **body.model_dump(exclude_unset=True))
    if user is None:
        raise NotFoundError("Пользователь не найден")
    return UserRead.model_validate(user)


@router.delete("/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT, dependencies=[Depends(require_permission("delete", "users"))])
async def delete_user(user_id: int, services: Services, current_user: CurrentUser) -> None:
    user = await UserRepository(services.session).get_by_id(user_id)
    if user is None:
        raise NotFoundError("Пользователь не найден")
    if user.is_superuser and not current_user.is_superuser:
        raise ForbiddenError("Нельзя удалить суперпользователя")
    await UserRepository(services.session).soft_delete(user_id, current_user.id)
