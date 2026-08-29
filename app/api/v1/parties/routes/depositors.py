# app/api/v1/parties/routes/depositors.py

"""Роутер для поклажедателей."""

from __future__ import annotations

from fastapi import APIRouter, Depends, status

from app.api.deps import ScopeDep, SessionDep, require_permission
from app.api.v1.parties.schemas import DepositorCreate, DepositorRead, DepositorUpdate
from app.core.exceptions import ForbiddenError, NotFoundError
from app.parties.repository import DepositorRepository
from app.parties.services.depositor_service import DepositorService

router = APIRouter(prefix="/depositors", tags=["depositors"])


def get_service(session: SessionDep) -> DepositorService:
    return DepositorService(DepositorRepository(session))


@router.get(
    "",
    response_model=list[DepositorRead],
    dependencies=[Depends(require_permission("view", "depositors"))],
)
async def list_depositors(
    scope: ScopeDep,
    service: DepositorService = Depends(get_service),
) -> list[DepositorRead]:
    return await service.list_all(scope=scope)


@router.post(
    "",
    response_model=DepositorRead,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_permission("create", "depositors"))],
)
async def create_depositor(
    body: DepositorCreate,
    scope: ScopeDep,
    service: DepositorService = Depends(get_service),
) -> DepositorRead:
    if scope.is_portal_user:
        raise ForbiddenError("Создание поклажедателя недоступно в портале")
    return await service.create(**body.model_dump())


@router.get(
    "/{id}",
    response_model=DepositorRead,
    dependencies=[Depends(require_permission("view", "depositors"))],
)
async def get_depositor(
    id: int,
    scope: ScopeDep,
    service: DepositorService = Depends(get_service),
) -> DepositorRead:
    row = await service.get_by_id(id, scope=scope)
    if row is None:
        raise NotFoundError("Поклажедатель не найден")
    return row


@router.patch(
    "/{id}",
    response_model=DepositorRead,
    dependencies=[Depends(require_permission("update", "depositors"))],
)
async def update_depositor(
    id: int,
    body: DepositorUpdate,
    scope: ScopeDep,
    service: DepositorService = Depends(get_service),
) -> DepositorRead:
    if scope.is_portal_user and not scope.allows_depositor(id):
        raise ForbiddenError("Нет доступа к поклажедателю")
    row = await service.update(id, **body.model_dump(exclude_unset=True))
    if row is None:
        raise NotFoundError("Поклажедатель не найден")
    return row


@router.delete(
    "/{id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(require_permission("delete", "depositors"))],
)
async def delete_depositor(
    id: int,
    scope: ScopeDep,
    service: DepositorService = Depends(get_service),
) -> None:
    if scope.is_portal_user:
        raise ForbiddenError("Удаление поклажедателя недоступно в портале")
    ok = await service.soft_delete(id)
    if not ok:
        raise NotFoundError("Поклажедатель не найден")
