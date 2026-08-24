"""API для ролей."""

from __future__ import annotations

from fastapi import APIRouter, Depends, status

from app.accounts.repository import RoleRepository
from app.accounts.services import RoleService
from app.api.deps import CurrentUser, Services, require_permission
from app.api.v1.accounts.schemas import RoleCreate, RoleRead
from app.core.exceptions import ConflictError, NotFoundError

router = APIRouter(tags=["roles"])


@router.get("/roles", response_model=list[RoleRead], dependencies=[Depends(require_permission("view", "roles"))])
async def list_roles(services: Services) -> list[RoleRead]:
    service = RoleService(RoleRepository(services.session))
    roles = await service.list_all()
    return [RoleRead.model_validate(r) for r in roles]


@router.post("/roles", response_model=RoleRead, status_code=status.HTTP_201_CREATED, dependencies=[Depends(require_permission("create", "roles"))])
async def create_role(body: RoleCreate, services: Services) -> RoleRead:
    service = RoleService(RoleRepository(services.session))
    try:
        role = await service.create(body.name, body.code, body.permissions)
    except ValueError as e:
        raise ConflictError(str(e)) from e
    return RoleRead.model_validate(role)


@router.get("/roles/{role_id}", response_model=RoleRead, dependencies=[Depends(require_permission("view", "roles"))])
async def get_role(role_id: int, services: Services) -> RoleRead:
    service = RoleService(RoleRepository(services.session))
    role = await service.get_by_id(role_id)
    if role is None:
        raise NotFoundError("Роль не найдена")
    return RoleRead.model_validate(role)


@router.patch("/roles/{role_id}", response_model=RoleRead, dependencies=[Depends(require_permission("update", "roles"))])
async def update_role(role_id: int, body: RoleCreate, services: Services) -> RoleRead:
    service = RoleService(RoleRepository(services.session))
    role = await service.update(role_id, **body.model_dump(exclude_unset=True))
    if role is None:
        raise NotFoundError("Роль не найдена")
    return RoleRead.model_validate(role)


@router.delete("/roles/{role_id}", status_code=status.HTTP_204_NO_CONTENT, dependencies=[Depends(require_permission("delete", "roles"))])
async def delete_role(role_id: int, services: Services, current_user: CurrentUser) -> None:
    role = await RoleRepository(services.session).get_by_id(role_id)
    if role is None:
        raise NotFoundError("Роль не найдена")
    await RoleRepository(services.session).soft_delete(role_id, current_user.id)
