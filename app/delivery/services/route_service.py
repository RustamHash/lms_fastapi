"""Сервис маршрутов."""

from __future__ import annotations

from app.delivery.models import Route
from app.delivery.repository import RouteRepository


class RouteService:
    def __init__(self, repo: RouteRepository) -> None:
        self._repo = repo

    async def get_by_id(self, route_id: int) -> Route | None:
        return await self._repo.get_by_id(route_id)

    async def list_all(self) -> list[Route]:
        return await self._repo.list_all()

    async def create(self, *, user_id: int | None = None, **kwargs) -> Route:
        return await self._repo.create(**kwargs)

    async def update(self, route_id: int, user_id: int | None = None, **kwargs) -> Route | None:
        return await self._repo.update(route_id, **kwargs)

    async def soft_delete(self, route_id: int, user_id: int | None = None) -> bool:
        return await self._repo.soft_delete(route_id, user_id)
