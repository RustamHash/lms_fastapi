"""Сервис файлов."""

from __future__ import annotations

from app.files.models import File
from app.files.repository import FileRepository


class FileService:
    def __init__(self, repo: FileRepository) -> None:
        self._repo = repo

    async def get_by_id(self, file_id: int) -> File | None:
        return await self._repo.get_by_id(file_id)

    async def list_all(self) -> list[File]:
        return await self._repo.list_all()

    async def create(self, *, user_id: int | None = None, **kwargs) -> File:
        return await self._repo.create(**kwargs)

    async def update(self, file_id: int, user_id: int | None = None, **kwargs) -> File | None:
        return await self._repo.update(file_id, **kwargs)

    async def soft_delete(self, file_id: int, user_id: int | None = None) -> bool:
        return await self._repo.soft_delete(file_id, user_id)
