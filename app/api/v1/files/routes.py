"""API для файлов."""

from __future__ import annotations

import os
from typing import Annotated
from uuid import uuid4

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from fastapi.responses import FileResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.files import schemas
from app.core.dependencies import get_current_user_id, get_session
from app.infrastructure.files.models import File as FileModel

router = APIRouter(prefix="/files", tags=["files"])

SessionDep = Annotated[AsyncSession, Depends(get_session)]
UserDep = Annotated[int | None, Depends(get_current_user_id)]

UPLOAD_DIR = "uploads"


@router.post("/upload", response_model=schemas.FileRead, status_code=status.HTTP_201_CREATED)
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

    with open(file_path, "wb") as f:
        f.write(content)

    file_model = FileModel(
        file_path=file_path,
        file_type=file_type,
        original_name=file.filename,
        size=len(content),
        mime_type=file.content_type or "",
        uploaded_by_id=user_id,
    )
    session.add(file_model)
    await session.flush()

    return schemas.FileRead.model_validate(file_model)


@router.get("", response_model=list[schemas.FileRead])
async def list_files(session: SessionDep) -> list[schemas.FileRead]:
    rows = list(await session.scalars(
        select(FileModel).where(FileModel.is_deleted.is_(False))
    ))
    return [schemas.FileRead.model_validate(r) for r in rows]


@router.get("/{file_id}", response_model=schemas.FileRead)
async def get_file(file_id: int, session: SessionDep) -> schemas.FileRead:
    file_model = await session.get(FileModel, file_id)
    if file_model is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Файл не найден")
    return schemas.FileRead.model_validate(file_model)


@router.get("/{file_id}/download")
async def download_file(file_id: int, session: SessionDep):
    file_model = await session.get(FileModel, file_id)
    if file_model is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Файл не найден")

    if not os.path.exists(file_model.file_path):
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Файл отсутствует на диске")

    return FileResponse(
        file_model.file_path,
        media_type=file_model.mime_type or "application/octet-stream",
        filename=file_model.original_name,
    )


@router.delete("/{file_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_file(file_id: int, session: SessionDep, user_id: UserDep) -> None:
    file_model = await session.get(FileModel, file_id)
    if file_model is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Файл не найден")
    file_model.soft_delete(user_id)
    await session.flush()
