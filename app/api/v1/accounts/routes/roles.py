"""API для ролей."""

from __future__ import annotations

from typing import NoReturn

from fastapi import APIRouter, Depends, status

from app.api.deps import CurrentUser, Services, require_permission
from app.api.v1.accounts.schemas import RoleCreate, RoleRead, RoleUpdate
from app.core.exceptions import BadRequestError, ConflictError, NotFoundError

router = APIRouter(tags=["roles"])


def _map_role_write_error(exc: ValueError) -> NoReturn:
    message = str(exc)
    if "уже существует" in message:
        raise ConflictError(message) from exc
    raise BadRequestError(message) from exc


@router.get("/roles", response_model=list[RoleRead], dependencies=[Depends(require_permission("view", "roles"))])
async def list_roles(services: Services) -> list[RoleRead]:
    roles = await services.role.list_all()
    return [RoleRead.model_validate(r) for r in roles]


@router.post("/roles", response_model=RoleRead, status_code=status.HTTP_201_CREATED, dependencies=[Depends(require_permission("create", "roles"))])
async def create_role(body: RoleCreate, services: Services) -> RoleRead:
    try:
        role = await services.role.create(body.name, body.code, body.permissions)
    except ValueError as e:
        _map_role_write_error(e)
    return RoleRead.model_validate(role)


@router.get("/roles/{role_id}", response_model=RoleRead, dependencies=[Depends(require_permission("view", "roles"))])
async def get_role(role_id: int, services: Services) -> RoleRead:
    role = await services.role.get_by_id(role_id)
    if role is None:
        raise NotFoundError("Роль не найдена")
    return RoleRead.model_validate(role)


@router.patch("/roles/{role_id}", response_model=RoleRead, dependencies=[Depends(require_permission("update", "roles"))])
async def update_role(role_id: int, body: RoleUpdate, services: Services) -> RoleRead:
    try:
        role = await services.role.update(role_id, **body.model_dump(exclude_unset=True))
    except ValueError as e:
        _map_role_write_error(e)
    if role is None:
        raise NotFoundError("Роль не найдена")
    return RoleRead.model_validate(role)


@router.delete("/roles/{role_id}", status_code=status.HTTP_204_NO_CONTENT, dependencies=[Depends(require_permission("delete", "roles"))])
async def delete_role(role_id: int, services: Services, current_user: CurrentUser) -> None:
    role = await services.role.get_by_id(role_id)
    if role is None:
        raise NotFoundError("Роль не найдена")
    await services.role.soft_delete(role_id, current_user.id)
