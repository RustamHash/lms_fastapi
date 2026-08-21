"""API для модуля documents."""

from __future__ import annotations

from fastapi import APIRouter, Depends, status

from app.api.deps import SessionDep, UserDep, require_permission
from app.api.v1.documents import schemas
from app.core.exceptions import BadRequestError, NotFoundError
from app.documents.models import Document
from app.documents.services import DocumentService

router = APIRouter(prefix="/documents", tags=["documents"])


@router.get("", response_model=list[schemas.DocumentRead], dependencies=[Depends(require_permission("view", "documents"))])
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


@router.post("", response_model=schemas.DocumentRead, status_code=status.HTTP_201_CREATED, dependencies=[Depends(require_permission("create", "documents"))])
async def create_document(
    body: schemas.DocumentCreate,
    session: SessionDep,
    user_id: UserDep,
) -> schemas.DocumentRead:
    service = DocumentService(session)
    doc = await service.create(user_id=user_id, **body.model_dump())
    return schemas.DocumentRead.model_validate(doc)


@router.get("/{document_id}", response_model=schemas.DocumentRead, dependencies=[Depends(require_permission("view", "documents"))])
async def get_document(document_id: int, session: SessionDep) -> schemas.DocumentRead:
    service = DocumentService(session)
    doc = await service.get_by_id(document_id)
    if doc is None:
        raise NotFoundError("Документ не найден")
    return schemas.DocumentRead.model_validate(doc)


@router.post("/{document_id}/lines", response_model=schemas.DocumentLineRead, status_code=status.HTTP_201_CREATED, dependencies=[Depends(require_permission("update", "documents"))])
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
        raise BadRequestError(str(e)) from e
    return schemas.DocumentLineRead.model_validate(line)


@router.get(
    "/{document_id}/lines",
    response_model=list[schemas.DocumentLineRead],
    dependencies=[Depends(require_permission("view", "documents"))],
)
async def list_document_lines(
    document_id: int,
    session: SessionDep,
) -> list[schemas.DocumentLineRead]:
    from sqlalchemy import select as sa_select
    from app.documents.models import DocumentLine

    rows = list(await session.scalars(
        sa_select(DocumentLine).where(DocumentLine.document_id == document_id)
    ))
    return [schemas.DocumentLineRead.model_validate(r) for r in rows]


@router.delete("/{document_id}", status_code=status.HTTP_204_NO_CONTENT, dependencies=[Depends(require_permission("delete", "documents"))])
async def delete_document(document_id: int, session: SessionDep, user_id: UserDep) -> None:
    doc = await session.get(Document, document_id)
    if doc is None:
        raise NotFoundError("Документ не найден")
    doc.soft_delete(user_id)
    await session.flush()


@router.get(
    "/lines/{line_id}",
    response_model=schemas.DocumentLineRead,
    dependencies=[Depends(require_permission("view", "documents"))],
)
async def get_document_line(
    line_id: int,
    session: SessionDep,
) -> schemas.DocumentLineRead:
    from app.documents.models import DocumentLine
    line = await session.get(DocumentLine, line_id)
    if line is None:
        raise NotFoundError("Строка документа не найдена")
    return schemas.DocumentLineRead.model_validate(line)


@router.patch(
    "/lines/{line_id}",
    response_model=schemas.DocumentLineRead,
    dependencies=[Depends(require_permission("update", "documents"))],
)
async def update_document_line(
    line_id: int,
    body: schemas.DocumentLineCreate,
    session: SessionDep,
    user_id: UserDep,
) -> schemas.DocumentLineRead:
    from app.documents.models import DocumentLine
    line = await session.get(DocumentLine, line_id)
    if line is None:
        raise NotFoundError("Строка документа не найдена")
    for field, value in body.model_dump(exclude_unset=True).items():
        setattr(line, field, value)
    line.updated_by_id = user_id
    await session.flush()
    return schemas.DocumentLineRead.model_validate(line)


@router.delete(
    "/lines/{line_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(require_permission("delete", "documents"))],
)
async def delete_document_line(
    line_id: int,
    session: SessionDep,
    user_id: UserDep,
) -> None:
    from app.documents.models import DocumentLine
    line = await session.get(DocumentLine, line_id)
    if line is None:
        raise NotFoundError("Строка документа не найдена")
    line.soft_delete(user_id)
    await session.flush()


@router.patch("/{document_id}/status", response_model=schemas.DocumentRead, dependencies=[Depends(require_permission("update", "documents"))])
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
        raise NotFoundError("Документ не найден")
    return schemas.DocumentRead.model_validate(doc)
