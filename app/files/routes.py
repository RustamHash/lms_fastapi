"""API для файлов."""

from __future__ import annotations

import os
from uuid import uuid4

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from fastapi.responses import FileResponse
from app.api.deps import SessionDep, UserDep, require_permission
from app.files import schemas
from app.core.exceptions import NotFoundError
from app.files.models import File as FileModel
from app.files.repository import FileRepository

router = APIRouter(prefix="/files", tags=["files"])

UPLOAD_DIR = "uploads"
ALLOWED_EXTENSIONS = {'.pdf', '.jpg', '.jpeg', '.png', '.doc', '.docx', '.xls', '.xlsx'}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB


@router.post("/upload", response_model=schemas.FileRead, status_code=status.HTTP_201_CREATED, dependencies=[Depends(require_permission("create", "files"))])
async def upload_file(
    file: UploadFile = File(...),
    file_type: str = "document_scan",
    session: SessionDep = None,
    user_id: UserDep = None,
) -> schemas.FileRead:
    if file.filename:
        ext = os.path.splitext(file.filename)[1].lower()
        if ext not in ALLOWED_EXTENSIONS:
            raise HTTPException(status_code=400, detail=f"Недопустимый тип файла")

    os.makedirs(UPLOAD_DIR, exist_ok=True)
    content = await file.read()

    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(status_code=413, detail="Файл слишком большой")

    filename = f"{uuid4().hex}_{os.path.splitext(file.filename)[1] if file.filename else ''}"
    file_path = os.path.join(UPLOAD_DIR, filename)

    with open(file_path, "wb") as f:
        f.write(content)

    file_model = await FileRepository(session).create(
        file_path=file_path,
        file_type=file_type,
        original_name=file.filename,
        size=len(content),
        mime_type=file.content_type or "",
        uploaded_by_id=user_id,
    )
    return schemas.FileRead.model_validate(file_model)


@router.get("", response_model=list[schemas.FileRead], dependencies=[Depends(require_permission("view", "files"))])
async def list_files(session: SessionDep) -> list[schemas.FileRead]:
    rows = await FileRepository(session).list_all()
    return [schemas.FileRead.model_validate(r) for r in rows]


@router.get("/{file_id}", response_model=schemas.FileRead, dependencies=[Depends(require_permission("view", "files"))])
async def get_file(file_id: int, session: SessionDep) -> schemas.FileRead:
    file_model = await FileRepository(session).get_by_id(file_id)
    if file_model is None:
        raise NotFoundError("Файл не найден")
    return schemas.FileRead.model_validate(file_model)


@router.get("/{file_id}/download")
async def download_file(file_id: int, session: SessionDep):
    file_model = await FileRepository(session).get_by_id(file_id)
    if file_model is None:
        raise NotFoundError("Файл не найден")

    upload_dir_abs = os.path.abspath(UPLOAD_DIR)
    file_path_abs = os.path.abspath(file_model.file_path)

    if not file_path_abs.startswith(upload_dir_abs):
        raise HTTPException(status_code=403, detail="Недопустимый путь к файлу")

    if not os.path.exists(file_path_abs):
        raise NotFoundError("Файл отсутствует на диске")

    return FileResponse(file_path_abs, media_type=file_model.mime_type or "application/octet-stream", filename=file_model.original_name)


@router.patch("/{file_id}", response_model=schemas.FileRead, dependencies=[Depends(require_permission("update", "files"))])
async def update_file(file_id: int, file_type: str | None = None, session: SessionDep = None, user_id: UserDep = None) -> schemas.FileRead:
    file_model = await FileRepository(session).get_by_id(file_id)
    if file_model is None:
        raise NotFoundError("Файл не найден")
    file_model = await FileRepository(session).update(file_id, file_type=file_type)
    return schemas.FileRead.model_validate(file_model)


@router.delete("/{file_id}", status_code=status.HTTP_204_NO_CONTENT, dependencies=[Depends(require_permission("delete", "files"))])
async def delete_file(file_id: int, session: SessionDep, user_id: UserDep) -> None:
    file_model = await FileRepository(session).get_by_id(file_id)
    if file_model is None:
        raise NotFoundError("Файл не найден")
    await FileRepository(session).soft_delete(file_id, user_id)
