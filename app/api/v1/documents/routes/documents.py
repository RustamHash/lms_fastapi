"""API для документов."""

from __future__ import annotations

from fastapi import APIRouter, Depends, status

from app.api.deps import Services, UserDep, require_permission
from app.api.v1.documents.schemas import (
    DocumentCreate,
    DocumentLineCreate,
    DocumentLineRead,
    DocumentRead,
)
from app.api.v1.warehouse.schemas.workflow import PlanFactRead
from app.core.exceptions import BadRequestError, NotFoundError
from app.documents.repository import DocumentLineRepository, DocumentRepository
from app.documents.services import DocumentService
from app.warehouse.repository import StockRepository

router = APIRouter(prefix="/documents", tags=["documents"])


@router.get("", response_model=list[DocumentRead], dependencies=[Depends(require_permission("view", "documents"))])
async def list_documents(services: Services, document_type: str | None = None) -> list[DocumentRead]:
    repo = DocumentRepository(services.session)
    if document_type:
        rows = await repo.list_by_type(document_type)
    else:
        rows = await repo.list_all()
    return [DocumentRead.model_validate(r) for r in rows]


@router.post("", response_model=DocumentRead, status_code=status.HTTP_201_CREATED, dependencies=[Depends(require_permission("create", "documents"))])
async def create_document(body: DocumentCreate, services: Services, user_id: UserDep) -> DocumentRead:
    service = DocumentService(DocumentRepository(services.session), DocumentLineRepository(services.session))
    doc = await service.create(user_id=user_id, **body.model_dump())
    return DocumentRead.model_validate(doc)


@router.get("/{document_id}", response_model=DocumentRead, dependencies=[Depends(require_permission("view", "documents"))])
async def get_document(document_id: int, services: Services) -> DocumentRead:
    service = DocumentService(DocumentRepository(services.session), DocumentLineRepository(services.session))
    doc = await service.get_by_id(document_id)
    if doc is None:
        raise NotFoundError("Документ не найден")
    return DocumentRead.model_validate(doc)


@router.get(
    "/{document_id}/plan-fact",
    response_model=PlanFactRead,
    dependencies=[Depends(require_permission("view", "documents"))],
)
async def document_plan_fact(document_id: int, services: Services) -> PlanFactRead:
    service = DocumentService(
        DocumentRepository(services.session), DocumentLineRepository(services.session)
    )
    doc = await service.get_by_id(document_id)
    if doc is None:
        raise NotFoundError("Документ не найден")
    data = await service.plan_fact(document_id, StockRepository(services.session))
    return PlanFactRead.model_validate(data)


@router.patch("/{document_id}", response_model=DocumentRead, dependencies=[Depends(require_permission("update", "documents"))])
async def update_document(document_id: int, body: DocumentCreate, services: Services, user_id: UserDep) -> DocumentRead:
    doc = await DocumentRepository(services.session).update(document_id, **body.model_dump(exclude_unset=True))
    if doc is None:
        raise NotFoundError("Документ не найден")
    return DocumentRead.model_validate(doc)


@router.delete("/{document_id}", status_code=status.HTTP_204_NO_CONTENT, dependencies=[Depends(require_permission("delete", "documents"))])
async def delete_document(document_id: int, services: Services, user_id: UserDep) -> None:
    ok = await DocumentRepository(services.session).soft_delete(document_id, user_id)
    if not ok:
        raise NotFoundError("Документ не найден")


@router.get("/{document_id}/lines", response_model=list[DocumentLineRead], dependencies=[Depends(require_permission("view", "documents"))])
async def list_document_lines(document_id: int, services: Services) -> list[DocumentLineRead]:
    rows = await DocumentLineRepository(services.session).list_by_document(document_id)
    return [DocumentLineRead.model_validate(r) for r in rows]


@router.post("/{document_id}/lines", response_model=DocumentLineRead, status_code=status.HTTP_201_CREATED, dependencies=[Depends(require_permission("update", "documents"))])
async def add_line(document_id: int, body: DocumentLineCreate, services: Services, user_id: UserDep) -> DocumentLineRead:
    service = DocumentService(DocumentRepository(services.session), DocumentLineRepository(services.session))
    try:
        line = await service.add_line(
            user_id=user_id,
            document_id=document_id,
            product_id=body.product_id,
            quantity=body.quantity,
            batch_id=body.batch_id,
        )
    except ValueError as e:
        raise BadRequestError(str(e)) from e
    return DocumentLineRead.model_validate(line)


@router.patch("/lines/{line_id}", response_model=DocumentLineRead, dependencies=[Depends(require_permission("update", "documents"))])
async def update_document_line(line_id: int, body: DocumentLineCreate, services: Services, user_id: UserDep) -> DocumentLineRead:
    line = await DocumentLineRepository(services.session).update(line_id, **body.model_dump(exclude_unset=True, exclude={"document_id"}))
    if line is None:
        raise NotFoundError("Строка документа не найдена")
    return DocumentLineRead.model_validate(line)


@router.delete("/lines/{line_id}", status_code=status.HTTP_204_NO_CONTENT, dependencies=[Depends(require_permission("delete", "documents"))])
async def delete_document_line(line_id: int, services: Services, user_id: UserDep) -> None:
    ok = await DocumentLineRepository(services.session).soft_delete(line_id, user_id)
    if not ok:
        raise NotFoundError("Строка документа не найдена")
