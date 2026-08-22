"""API для модуля documents."""

from __future__ import annotations

from fastapi import HTTPException, APIRouter, Depends, status

from app.api.deps import SessionDep, UserDep, require_permission
from app.api.v1.documents import schemas
from app.core.exceptions import BadRequestError, NotFoundError
from app.documents.models import Document
from app.documents.services import DocumentService
from app.core.statuses import DocumentStatus
from app.documents.document_types import DocumentType
from app.documents.repository import DocumentLineRepository, DocumentRepository

router = APIRouter(prefix="/documents", tags=["documents"])


@router.get("/list", response_model=list[schemas.DocumentList], dependencies=[Depends(require_permission("view", "documents"))])
async def list_documents_for_table(session: SessionDep,
) -> list[schemas.DocumentList]:
    """Плоский список для таблицы."""
    from sqlalchemy.orm import selectinload
    from app.warehouse.models import Warehouse
    
    # Загружаем документы с warehouse за один запрос
    stmt = select(Document).options(selectinload(Document.warehouse))
    rows = list(await session.scalars(stmt))

    result = []
    for r in rows:
        result.append(schemas.DocumentList(
            id=r.id,
            is_active=r.is_active,
            is_deleted=r.is_deleted,
            created_at=r.created_at,
            updated_at=r.updated_at,
            created_by_id=r.created_by_id,
            updated_by_id=r.updated_by_id,
            deleted_at=r.deleted_at,
            deleted_by_id=r.deleted_by_id,
            document_number=r.document_number,
            document_type=r.document_type,
            document_type_label=DocumentType(r.document_type).label if r.document_type in DocumentType._value2member_map_ else r.document_type,
            document_date=r.document_date,
            delivery_date=r.delivery_date,
            status=r.status,
            status_label=DocumentStatus(r.status).label if r.status in DocumentStatus._value2member_map_ else r.status,
            warehouse_name=r.warehouse.name if r.warehouse else None,
        ))
    return result


@router.get("/{document_id}/detail", response_model=schemas.DocumentDetail, dependencies=[Depends(require_permission("view", "documents"))])
async def get_document_detail(document_id: int, session: SessionDep) -> schemas.DocumentDetail:
    """Вложенная схема для детальной страницы."""
    doc_service = DocumentService(DocumentRepository(session), DocumentLineRepository(session))
    doc = await doc_service.get_by_id(document_id)
    if doc is None:
        raise NotFoundError("Документ не найден")
    return schemas.DocumentDetail.model_validate(doc)


@router.get("", response_model=list[schemas.DocumentRead], dependencies=[Depends(require_permission("view", "documents"))])
async def list_documents(
    session: SessionDep,
    document_type: str | None = None,
) -> list[schemas.DocumentRead]:
    service = DocumentService(DocumentRepository(session), DocumentLineRepository(session))
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
    service = DocumentService(DocumentRepository(session), DocumentLineRepository(session))
    doc = await service.create(user_id=user_id, **body.model_dump())
    return schemas.DocumentRead.model_validate(doc)


@router.get("/{document_id}", response_model=schemas.DocumentRead, dependencies=[Depends(require_permission("view", "documents"))])
async def get_document(document_id: int, session: SessionDep) -> schemas.DocumentRead:
    service = DocumentService(DocumentRepository(session), DocumentLineRepository(session))
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
    service = DocumentService(DocumentRepository(session), DocumentLineRepository(session))
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
    rows = await DocumentLineRepository(session).list_by_document(document_id)
    return [schemas.DocumentLineRead.model_validate(r) for r in rows]


@router.patch("/{document_id}", response_model=schemas.DocumentRead, dependencies=[Depends(require_permission("update", "documents"))])
async def update_document(
    document_id: int,
    body: schemas.DocumentCreate,
    session: SessionDep,
    user_id: UserDep,
) -> schemas.DocumentRead:
    """Обновить документ."""
    doc = await DocumentRepository(session).get_by_id(document_id)
    if doc is None:
        raise NotFoundError("Документ не найден")
    for field, value in body.model_dump(exclude_unset=True).items():
        setattr(doc, field, value)
    doc.updated_by_id = user_id
    try:
        await session.flush()
    except Exception as e:
        await session.rollback()
        raise HTTPException(status_code=500, detail=f"Ошибка базы данных: {e}")
    return schemas.DocumentRead.model_validate(doc)


@router.delete("/{document_id}", status_code=status.HTTP_204_NO_CONTENT, dependencies=[Depends(require_permission("delete", "documents"))])
async def delete_document(document_id: int, session: SessionDep, user_id: UserDep) -> None:
    doc = await DocumentRepository(session).get_by_id(document_id)
    if doc is None:
        raise NotFoundError("Документ не найден")
    doc.soft_delete(user_id)
    try:
        await session.flush()
    except Exception as e:
        await session.rollback()
        raise HTTPException(status_code=500, detail=f"Ошибка базы данных: {e}")


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
    line = await DocumentLineRepository(session).get_by_id(line_id)
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
    line = await DocumentLineRepository(session).get_by_id(line_id)
    if line is None:
        raise NotFoundError("Строка документа не найдена")
    for field, value in body.model_dump(exclude_unset=True).items():
        setattr(line, field, value)
    line.updated_by_id = user_id
    try:
        await session.flush()
    except Exception as e:
        await session.rollback()
        raise HTTPException(status_code=500, detail=f"Ошибка базы данных: {e}")
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
    line = await DocumentLineRepository(session).get_by_id(line_id)
    if line is None:
        raise NotFoundError("Строка документа не найдена")
    line.soft_delete(user_id)
    try:
        await session.flush()
    except Exception as e:
        await session.rollback()
        raise HTTPException(status_code=500, detail=f"Ошибка базы данных: {e}")


@router.patch("/{document_id}/status", response_model=schemas.DocumentRead, dependencies=[Depends(require_permission("update", "documents"))])
async def update_status(
    document_id: int,
    body: schemas.DocumentStatusUpdate,
    session: SessionDep,
    user_id: UserDep,
) -> schemas.DocumentRead:
    service = DocumentService(DocumentRepository(session), DocumentLineRepository(session))
    doc = await service.set_status(
        user_id=user_id,
        document_id=document_id,
        status=body.status,
    )
    if doc is None:
        raise NotFoundError("Документ не найден")
    return schemas.DocumentRead.model_validate(doc)
