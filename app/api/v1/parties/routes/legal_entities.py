# app/api/v1/parties/routes/legal_entities.py

"""Роутер для юрлиц."""

from __future__ import annotations

from fastapi import APIRouter, Depends, status

from app.api.deps import SessionDep, require_permission
from app.api.v1.parties.schemas import LegalEntityCreate, LegalEntityRead, LegalEntityUpdate
from app.core.exceptions import NotFoundError
from app.parties.repository import LegalEntityRepository
from app.parties.services.legal_entity_service import LegalEntityService

router = APIRouter(prefix="/legal-entities", tags=["legal-entities"])


def get_service(session: SessionDep) -> LegalEntityService:
    return LegalEntityService(LegalEntityRepository(session))


@router.get("", response_model=list[LegalEntityRead], dependencies=[Depends(require_permission("view", "legal_entities"))])
async def list_legal_entities(service: LegalEntityService = Depends(get_service)) -> list[LegalEntityRead]:
    return await service.list_all()


@router.post("", response_model=LegalEntityRead, status_code=status.HTTP_201_CREATED, dependencies=[Depends(require_permission("create", "legal_entities"))])
async def create_legal_entity(body: LegalEntityCreate, service: LegalEntityService = Depends(get_service)) -> LegalEntityRead:
    return await service.create(**body.model_dump())


@router.get("/{id}", response_model=LegalEntityRead, dependencies=[Depends(require_permission("view", "legal_entities"))])
async def get_legal_entity(id: int, service: LegalEntityService = Depends(get_service)) -> LegalEntityRead:
    row = await service.get_by_id(id)
    if row is None:
        raise NotFoundError("Юрлицо не найдено")
    return row


@router.patch("/{id}", response_model=LegalEntityRead, dependencies=[Depends(require_permission("update", "legal_entities"))])
async def update_legal_entity(id: int, body: LegalEntityUpdate, service: LegalEntityService = Depends(get_service)) -> LegalEntityRead:
    row = await service.update(id, **body.model_dump(exclude_unset=True))
    if row is None:
        raise NotFoundError("Юрлицо не найдено")
    return row


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT, dependencies=[Depends(require_permission("delete", "legal_entities"))])
async def delete_legal_entity(id: int, service: LegalEntityService = Depends(get_service)) -> None:
    ok = await service.soft_delete(id)
    if not ok:
        raise NotFoundError("Юрлицо не найдено")
