"""Сервис отклонений."""

from __future__ import annotations

from app.delivery.models import DeliveryDeviation
from app.delivery.repository import DeviationRepository


class DeviationService:
    def __init__(self, repo: DeviationRepository) -> None:
        self._repo = repo

    async def get_by_id(self, deviation_id: int) -> DeliveryDeviation | None:
        return await self._repo.get_by_id(deviation_id)

    async def list_all(self) -> list[DeliveryDeviation]:
        return await self._repo.list_all()

    async def list_by_order(self, order_id: int) -> list[DeliveryDeviation]:
        return await self._repo.list_by_order(order_id)

    async def create(self, *, user_id: int | None = None, **kwargs) -> DeliveryDeviation:
        return await self._repo.create(**kwargs)

    async def update(self, deviation_id: int, user_id: int | None = None, **kwargs) -> DeliveryDeviation | None:
        return await self._repo.update(deviation_id, **kwargs)

    async def soft_delete(self, deviation_id: int, user_id: int | None = None) -> bool:
        return await self._repo.soft_delete(deviation_id, user_id)
