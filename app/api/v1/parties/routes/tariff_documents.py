# app/api/v1/parties/routes/tariff_documents.py

"""Роутер для тарифных документов."""

from __future__ import annotations

from fastapi import APIRouter, Depends, status

from app.api.deps import SessionDep, require_permission
from app.api.v1.parties.schemas import TariffDocumentCreate, TariffDocumentRead, TariffDocumentUpdate
from app.core.exceptions import NotFoundError
from app.parties.repository import TariffDocumentRepository
from app.parties.services.tariff_document_service import TariffDocumentService

router = APIRouter(prefix="/tariff-documents", tags=["tariff-documents"])


def get_service(session: SessionDep) -> TariffDocumentService:
    return TariffDocumentService(TariffDocumentRepository(session))


@router.get("", response_model=list[TariffDocumentRead], dependencies=[Depends(require_permission("view", "tariffs"))])
async def list_tariff_documents(service: TariffDocumentService = Depends(get_service)) -> list[TariffDocumentRead]:
    return await service.list_all()


@router.post("", response_model=TariffDocumentRead, status_code=status.HTTP_201_CREATED, dependencies=[Depends(require_permission("create", "tariffs"))])
async def create_tariff_document(body: TariffDocumentCreate, service: TariffDocumentService = Depends(get_service)) -> TariffDocumentRead:
    return await service.create(**body.model_dump())


@router.get("/{id}", response_model=TariffDocumentRead, dependencies=[Depends(require_permission("view", "tariffs"))])
async def get_tariff_document(id: int, service: TariffDocumentService = Depends(get_service)) -> TariffDocumentRead:
    row = await service.get_by_id(id)
    if row is None:
        raise NotFoundError("Тарифный документ не найден")
    return row


@router.patch("/{id}", response_model=TariffDocumentRead, dependencies=[Depends(require_permission("update", "tariffs"))])
async def update_tariff_document(id: int, body: TariffDocumentUpdate, service: TariffDocumentService = Depends(get_service)) -> TariffDocumentRead:
    row = await service.update(id, **body.model_dump(exclude_unset=True))
    if row is None:
        raise NotFoundError("Тарифный документ не найден")
    return row


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT, dependencies=[Depends(require_permission("delete", "tariffs"))])
async def delete_tariff_document(id: int, service: TariffDocumentService = Depends(get_service)) -> None:
    ok = await service.soft_delete(id)
    if not ok:
        raise NotFoundError("Тарифный документ не найден")
