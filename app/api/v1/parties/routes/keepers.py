# app/api/v1/parties/routes/keepers.py

"""Роутер для хранителей."""

from __future__ import annotations

from fastapi import APIRouter, Depends, status

from app.api.deps import SessionDep, require_permission
from app.api.v1.parties.schemas import KeeperCreate, KeeperRead, KeeperUpdate
from app.core.exceptions import NotFoundError
from app.parties.repository import KeeperRepository
from app.parties.services.keeper_service import KeeperService

router = APIRouter(prefix="/keepers", tags=["keepers"])


def get_service(session: SessionDep) -> KeeperService:
    return KeeperService(KeeperRepository(session))


@router.get("", response_model=list[KeeperRead], dependencies=[Depends(require_permission("view", "keepers"))])
async def list_keepers(service: KeeperService = Depends(get_service)) -> list[KeeperRead]:
    return await service.list_all()


@router.post("", response_model=KeeperRead, status_code=status.HTTP_201_CREATED, dependencies=[Depends(require_permission("create", "keepers"))])
async def create_keeper(body: KeeperCreate, service: KeeperService = Depends(get_service)) -> KeeperRead:
    return await service.create(**body.model_dump())


@router.get("/{id}", response_model=KeeperRead, dependencies=[Depends(require_permission("view", "keepers"))])
async def get_keeper(id: int, service: KeeperService = Depends(get_service)) -> KeeperRead:
    row = await service.get_by_id(id)
    if row is None:
        raise NotFoundError("Хранитель не найден")
    return row


@router.patch("/{id}", response_model=KeeperRead, dependencies=[Depends(require_permission("update", "keepers"))])
async def update_keeper(id: int, body: KeeperUpdate, service: KeeperService = Depends(get_service)) -> KeeperRead:
    row = await service.update(id, **body.model_dump(exclude_unset=True))
    if row is None:
        raise NotFoundError("Хранитель не найден")
    return row


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT, dependencies=[Depends(require_permission("delete", "keepers"))])
async def delete_keeper(id: int, service: KeeperService = Depends(get_service)) -> None:
    ok = await service.soft_delete(id)
    if not ok:
        raise NotFoundError("Хранитель не найден")
