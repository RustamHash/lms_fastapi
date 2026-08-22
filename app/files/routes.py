"""API для файлов."""

from __future__ import annotations

import os
from uuid import uuid4
import aiofiles

from fastapi import HTTPException, APIRouter, Depends, File, UploadFile, status
from fastapi.responses import FileResponse
from sqlalchemy import select

from app.api.deps import SessionDep, UserDep, require_permission
from app.files import schemas
from app.core.exceptions import NotFoundError
from app.files.models import File as FileModel

router = APIRouter(prefix="/files", tags=["files"])

UPLOAD_DIR = "uploads"


@router.post("/upload", response_model=schemas.FileRead, status_code=status.HTTP_201_CREATED, dependencies=[Depends(require_permission("create", "files"))])
async def upload_file(
    file: UploadFile = File(...),
    file_type: str = "document_scan",
    session: SessionDep = None,
    user_id: UserDep = None,
) -> schemas.FileRead:
    os.makedirs(UPLOAD_DIR, exist_ok=True)

    content = await file.read()
    filename = f"{uuid4().hex}_{file.filename}"
    file_path = os.path.join(UPLOAD_DIR, filename)

    async with aiofiles.open(file_path, "wb") as f:
        await f.write(content)

    file_model = FileModel(
        file_path=file_path,
        file_type=file_type,
        original_name=file.filename,
        size=len(content),
        mime_type=file.content_type or "",
        uploaded_by_id=user_id,
    )
    session.add(file_model)
    try:
        await session.flush()
    except Exception as e:
        await session.rollback()
        raise HTTPException(status_code=500, detail=f"Ошибка базы данных: {e}")

    return schemas.FileRead.model_validate(file_model)


@router.post("", response_model=schemas.FileRead, status_code=status.HTTP_201_CREATED, dependencies=[Depends(require_permission("create", "files"))])
async def create_file(
    file: UploadFile = File(...),
    file_type: str = "document_scan",
    session: SessionDep = None,
    user_id: UserDep = None,
) -> schemas.FileRead:
    """Загрузить файл."""
    import os
    from uuid import uuid4
    
    os.makedirs(UPLOAD_DIR, exist_ok=True)
    content_data = await file.read()
    filename = f"{uuid4().hex}_{file.filename}"
    file_path = os.path.join(UPLOAD_DIR, filename)
    
    with open(file_path, "wb") as f:
        f.write(content_data)
    
    file_model = FileModel(
        file_path=file_path,
        file_type=file_type,
        original_name=file.filename,
        size=len(content_data),
        mime_type=file.content_type or "",
        uploaded_by_id=user_id,
    )
    session.add(file_model)
    try:
        await session.flush()
    except Exception as e:
        await session.rollback()
        raise HTTPException(status_code=500, detail=f"Ошибка базы данных: {e}")
    
    return schemas.FileRead.model_validate(file_model)


@router.get("", response_model=list[schemas.FileRead], dependencies=[Depends(require_permission("view", "files"))])
async def list_files(session: SessionDep) -> list[schemas.FileRead]:
    rows = list(await session.scalars(
        select(FileModel)
    ))
    return [schemas.FileRead.model_validate(r) for r in rows]


@router.get("/{file_id}", response_model=schemas.FileRead, dependencies=[Depends(require_permission("view", "files"))])
async def get_file(file_id: int, session: SessionDep) -> schemas.FileRead:
    file_model = await session.get(FileModel, file_id)
    if file_model is None:
        raise NotFoundError("Файл не найден")
    return schemas.FileRead.model_validate(file_model)


@router.get("/{file_id}/download")
async def download_file(file_id: int, session: SessionDep):
    file_model = await session.get(FileModel, file_id)
    if file_model is None:
        raise NotFoundError("Файл не найден")

    if not os.path.exists(file_model.file_path):
        raise NotFoundError("Файл отсутствует на диске")

    return FileResponse(
        file_model.file_path,
        media_type=file_model.mime_type or "application/octet-stream",
        filename=file_model.original_name,
    )


@router.patch(
    "/{file_id}",
    response_model=schemas.FileRead,
    dependencies=[Depends(require_permission("update", "files"))],
)
async def update_file(
    file_id: int,
    file_type: str | None = None,
    session: SessionDep = None,
    user_id: UserDep = None,
) -> schemas.FileRead:
    file_model = await session.get(FileModel, file_id)
    if file_model is None:
        raise NotFoundError("Файл не найден")
    if file_type:
        file_model.file_type = file_type
    file_model.updated_by_id = user_id
    try:
        await session.flush()
    except Exception as e:
        await session.rollback()
        raise HTTPException(status_code=500, detail=f"Ошибка базы данных: {e}")
    return schemas.FileRead.model_validate(file_model)


@router.delete("/{file_id}", status_code=status.HTTP_204_NO_CONTENT, dependencies=[Depends(require_permission("delete", "files"))])
async def delete_file(file_id: int, session: SessionDep, user_id: UserDep) -> None:
    file_model = await session.get(FileModel, file_id)
    if file_model is None:
        raise NotFoundError("Файл не найден")
    file_model.soft_delete(user_id)
    try:
        await session.flush()
    except Exception as e:
        await session.rollback()
        raise HTTPException(status_code=500, detail=f"Ошибка базы данных: {e}")
