"""Сервис товаров."""

from __future__ import annotations

from decimal import Decimal

import logging

from app.warehouse.repository import ProductRepository
from app.warehouse.models import Package

logger = logging.getLogger(__name__)


class ProductService:
    def __init__(self, repo: ProductRepository) -> None:
        self._repo = repo

    async def create(self, *, user_id: int, depositor_id: int, external_id: str, name: str, **kwargs) -> object:
        existing = await self._repo.get_by_external_id(depositor_id, external_id)
        if existing:
            raise ValueError(f"Товар с кодом {external_id} уже существует")

        logger.info("Создание товара: %s", external_id)
        product = await self._repo.create(
            depositor_id=depositor_id,
            external_id=external_id,
            name=name,
            **kwargs,
        )

        # Базовая упаковка
        base_package = Package(
            product_id=product.id,
            name="шт",
            quantity=1,
            is_base_unit=True,
        )
        self._repo._s.add(base_package)
        await self._repo._s.flush()

        logger.info("Товар создан: id=%s", product.id)
        return product

    async def get_by_id(self, product_id: int):
        return await self._repo.get_by_id(product_id)

    async def get_or_create(self, depositor_id: int, external_id: str, defaults: dict, user_id: int | None = None):
        product = await self._repo.get_by_external_id(depositor_id, external_id)
        if product:
            return product, False

        product = await self.create(
            user_id=user_id,
            depositor_id=depositor_id,
            external_id=external_id,
            name=defaults.get("name", external_id),
            sku=defaults.get("sku", external_id),
            legal_name=defaults.get("legal_name", ""),
            weight=defaults.get("weight", Decimal("0")),
            volume=defaults.get("volume", Decimal("0")),
            price=defaults.get("price"),
            shelf_life_days=defaults.get("shelf_life_days"),
            min_shelf_life_days=defaults.get("min_shelf_life_days"),
        )
        return product, True

    async def list_by_depositor(self, depositor_id: int):
        return await self._repo.list_by_depositor(depositor_id)

    async def list_all(self):
        return await self._repo.list_all()

    async def update(self, product_id: int, user_id: int, **fields):
        return await self._repo.update(product_id, **fields)

    async def soft_delete(self, product_id: int, user_id: int | None = None) -> bool:
        product = await self.get_by_id(product_id)
        if not product:
            return False
        product.soft_delete(user_id)
        await self._repo._s.flush()
        return True
