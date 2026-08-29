"""Сервис товаров."""

from __future__ import annotations

from decimal import Decimal

import logging

from app.warehouse.models import Product, Package
from app.warehouse.repository import ProductRepository
from app.accounts.scope import DataScope

logger = logging.getLogger(__name__)


class ProductService:
    def __init__(self, repo: ProductRepository) -> None:
        self._repo = repo

    async def get_by_id(
        self, product_id: int, scope: DataScope | None = None
    ) -> Product | None:
        return await self._repo.get_by_id(product_id, scope=scope)

    async def list_all(self, scope: DataScope | None = None) -> list[Product]:
        return await self._repo.list_all(scope=scope)

    async def list_by_depositor(
        self, depositor_id: int, scope: DataScope | None = None
    ) -> list[Product]:
        return await self._repo.list_by_depositor(depositor_id, scope=scope)

    async def get_by_external_id(self, depositor_id: int, external_id: str) -> Product | None:
        return await self._repo.get_by_external_id(depositor_id, external_id)

    async def create(self, *, user_id: int | None = None, depositor_id: int, external_id: str, name: str, **kwargs) -> Product:
        existing = await self._repo.get_by_external_id(depositor_id, external_id)
        if existing:
            raise ValueError(f"Товар с кодом {external_id} уже существует")

        # Извлекаем поля для упаковки
        unit = kwargs.pop("unit", "шт")
        barcode = kwargs.pop("barcode", None)
        gross_mass = kwargs.pop("gross_mass", None)

        product = await self._repo.create(
            depositor_id=depositor_id,
            external_id=external_id,
            name=name,
            **kwargs,
        )

        # Базовая упаковка
        base_package = Package(
            product_id=product.id,
            name=unit,
            quantity=1,
            barcode=barcode,
            weight=gross_mass or kwargs.get("weight"),
            is_base_unit=True,
        )
        self._repo._s.add(base_package)
        await self._repo._s.flush()

        return product

    async def get_or_create(
        self, depositor_id: int, external_id: str, defaults: dict, user_id: int | None = None
    ) -> tuple[Product, bool]:
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
            unit=defaults.get("unit"),
            barcode=defaults.get("barcode"),
            gross_mass=defaults.get("gross_mass"),
        )
        return product, True

    async def update(self, product_id: int, user_id: int | None = None, **kwargs) -> Product | None:
        return await self._repo.update(product_id, **kwargs)

    async def soft_delete(self, product_id: int, user_id: int | None = None) -> bool:
        return await self._repo.soft_delete(product_id, user_id)
