"""API для модуля documents."""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.documents import schemas
from app.core.dependencies import get_current_user_id, get_session
from app.documents.services import DocumentService

router = APIRouter(prefix="/documents", tags=["documents"])

SessionDep = Annotated[AsyncSession, Depends(get_session)]
UserDep = Annotated[int | None, Depends(get_current_user_id)]


@router.get("", response_model=list[schemas.DocumentRead])
async def list_documents(
    session: SessionDep,
    document_type: str | None = None,
) -> list[schemas.DocumentRead]:
    service = DocumentService(session)
    if document_type:
        rows = await service.list_by_type(document_type)
    else:
        rows = await service.list_all()
    return [schemas.DocumentRead.model_validate(r) for r in rows]


@router.post("", response_model=schemas.DocumentRead, status_code=status.HTTP_201_CREATED)
async def create_document(
    body: schemas.DocumentCreate,
    session: SessionDep,
    user_id: UserDep,
) -> schemas.DocumentRead:
    service = DocumentService(session)
    doc = await service.create(user_id=user_id, **body.model_dump())
    return schemas.DocumentRead.model_validate(doc)


@router.get("/{document_id}", response_model=schemas.DocumentRead)
async def get_document(document_id: int, session: SessionDep) -> schemas.DocumentRead:
    service = DocumentService(session)
    doc = await service.get_by_id(document_id)
    if doc is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Документ не найден")
    return schemas.DocumentRead.model_validate(doc)


@router.post("/{document_id}/lines", response_model=schemas.DocumentLineRead, status_code=status.HTTP_201_CREATED)
async def add_line(
    document_id: int,
    body: schemas.DocumentLineCreate,
    session: SessionDep,
    user_id: UserDep,
) -> schemas.DocumentLineRead:
    service = DocumentService(session)
    try:
        line = await service.add_line(
            user_id=user_id,
            document_id=document_id,
            product_id=body.product_id,
            quantity=body.quantity,
            batch_id=body.batch_id,
        )
    except ValueError as e:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, detail=str(e)) from e
    return schemas.DocumentLineRead.model_validate(line)


@router.delete("/{document_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_document(document_id: int, session: SessionDep, user_id: UserDep) -> None:
    from app.documents.models import Document
    doc = await session.get(Document, document_id)
    if doc is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Документ не найден")
    doc.soft_delete(user_id)
    await session.flush()


@router.patch("/{document_id}/status", response_model=schemas.DocumentRead)
async def update_status(
    document_id: int,
    body: schemas.DocumentStatusUpdate,
    session: SessionDep,
    user_id: UserDep,
) -> schemas.DocumentRead:
    service = DocumentService(session)
    doc = await service.set_status(
        user_id=user_id,
        document_id=document_id,
        status=body.status,
    )
    if doc is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Документ не найден")
    return schemas.DocumentRead.model_validate(doc)
