"""API для файлов."""

from __future__ import annotations

import os
from uuid import uuid4

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from fastapi.responses import FileResponse

from app.api.deps import SessionDep, UserDep, require_permission
from app.core.exceptions import NotFoundError
from app.files import schemas
from app.files.repository import FileRepository
from app.files.services.file_service import FileService

router = APIRouter(prefix="/files", tags=["files"])

UPLOAD_DIR = "uploads"
ALLOWED_EXTENSIONS = {".pdf", ".jpg", ".jpeg", ".png", ".doc", ".docx", ".xls", ".xlsx"}
MAX_FILE_SIZE = 10 * 1024 * 1024


def get_service(session: SessionDep) -> FileService:
    return FileService(FileRepository(session))


def _safe_disk_path(stored_path: str) -> str:
    upload_dir_abs = os.path.abspath(UPLOAD_DIR)
    file_path_abs = os.path.abspath(stored_path)
    if os.path.commonpath([upload_dir_abs, file_path_abs]) != upload_dir_abs:
        raise HTTPException(status_code=403, detail="Недопустимый путь к файлу")
    return file_path_abs


@router.post(
    "/upload",
    response_model=schemas.FileRead,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_permission("create", "files"))],
)
async def upload_file(
    file: UploadFile = File(...),
    file_type: str = "document_scan",
    service: FileService = Depends(get_service),
    user_id: UserDep = None,
) -> schemas.FileRead:
    ext = os.path.splitext(file.filename)[1].lower() if file.filename else ""
    if ext and ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(status_code=400, detail="Недопустимый тип файла")

    os.makedirs(UPLOAD_DIR, exist_ok=True)
    content = await file.read()

    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(status_code=413, detail="Файл слишком большой")

    filename = f"{uuid4().hex}{ext}"
    file_path = os.path.join(UPLOAD_DIR, filename)

    with open(file_path, "wb") as out:
        out.write(content)

    file_model = await service.create(
        user_id=user_id,
        file_path=file_path,
        file_type=file_type,
        original_name=file.filename or filename,
        size=len(content),
        mime_type=file.content_type or "",
        uploaded_by_id=user_id,
    )
    return schemas.FileRead.model_validate(file_model)


@router.get(
    "",
    response_model=list[schemas.FileRead],
    dependencies=[Depends(require_permission("view", "files"))],
)
async def list_files(service: FileService = Depends(get_service)) -> list[schemas.FileRead]:
    rows = await service.list_all()
    return [schemas.FileRead.model_validate(r) for r in rows]


@router.get(
    "/{file_id}",
    response_model=schemas.FileRead,
    dependencies=[Depends(require_permission("view", "files"))],
)
async def get_file(file_id: int, service: FileService = Depends(get_service)) -> schemas.FileRead:
    file_model = await service.get_by_id(file_id)
    if file_model is None:
        raise NotFoundError("Файл не найден")
    return schemas.FileRead.model_validate(file_model)


@router.get(
    "/{file_id}/download",
    dependencies=[Depends(require_permission("view", "files"))],
)
async def download_file(file_id: int, service: FileService = Depends(get_service)):
    file_model = await service.get_by_id(file_id)
    if file_model is None:
        raise NotFoundError("Файл не найден")

    file_path_abs = _safe_disk_path(file_model.file_path)
    if not os.path.exists(file_path_abs):
        raise NotFoundError("Файл отсутствует на диске")

    return FileResponse(
        file_path_abs,
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
    service: FileService = Depends(get_service),
) -> schemas.FileRead:
    if file_type is None:
        file_model = await service.get_by_id(file_id)
    else:
        file_model = await service.update(file_id, file_type=file_type)
    if file_model is None:
        raise NotFoundError("Файл не найден")
    return schemas.FileRead.model_validate(file_model)


@router.delete(
    "/{file_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(require_permission("delete", "files"))],
)
async def delete_file(
    file_id: int,
    service: FileService = Depends(get_service),
    user_id: UserDep = None,
) -> None:
    ok = await service.soft_delete(file_id, user_id)
    if not ok:
        raise NotFoundError("Файл не найден")
