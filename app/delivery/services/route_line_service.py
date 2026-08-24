"""Сервис строк маршрутов."""

from __future__ import annotations

from app.delivery.models import RouteLine
from app.delivery.repository import RouteLineRepository


class RouteLineService:
    def __init__(self, repo: RouteLineRepository) -> None:
        self._repo = repo

    async def get_by_id(self, line_id: int) -> RouteLine | None:
        return await self._repo.get_by_id(line_id)

    async def list_all(self) -> list[RouteLine]:
        return await self._repo.list_all()

    async def list_by_route(self, route_id: int) -> list[RouteLine]:
        return await self._repo.list_by_route(route_id)

    async def create(self, *, user_id: int | None = None, **kwargs) -> RouteLine:
        return await self._repo.create(**kwargs)

    async def update(self, line_id: int, user_id: int | None = None, **kwargs) -> RouteLine | None:
        return await self._repo.update(line_id, **kwargs)

    async def soft_delete(self, line_id: int, user_id: int | None = None) -> bool:
        return await self._repo.soft_delete(line_id, user_id)
