"""Сервис товаров."""

from __future__ import annotations

from decimal import Decimal

import logging

from sqlalchemy import select

logger = logging.getLogger(__name__)
from sqlalchemy.ext.asyncio import AsyncSession

from app.warehouse.models import Product, ProductGroup, Package


class ProductService:
    def __init__(self, session: AsyncSession) -> None:
        self._s = session

    async def create(
        self,
        *,
        depositor_id: int,
        external_id: str,
        name: str,
        sku: str = "",
        group_id: int | None = None,
        legal_name: str = "",
        weight: Decimal = Decimal("0"),
        volume: Decimal = Decimal("0"),
        price: Decimal | None = None,
        shelf_life_days: int | None = None,
        min_shelf_life_days: int | None = None,
        is_marked: bool = False,
        is_serial_tracked: bool = False,
        is_batch_tracked: bool = False,
        is_expiration_tracked: bool = False,
        temperature_requirements: str = "",
        user_id: int | None = None,
    ) -> Product:
        stmt = select(Product).where(
            Product.depositor_id == depositor_id,
            Product.external_id == external_id,
        )
        existing = await self._s.scalar(stmt)
        if existing:
            raise ValueError(f"Товар с кодом {external_id} уже существует")

        logger.info("Создание товара: %s", external_id)
        product = Product(
            depositor_id=depositor_id,
            external_id=external_id,
            name=name,
            sku=sku or external_id,
            group_id=group_id,
            legal_name=legal_name,
            weight=weight,
            volume=volume,
            price=price,
            shelf_life_days=shelf_life_days,
            min_shelf_life_days=min_shelf_life_days,
            is_marked=is_marked,
            is_serial_tracked=is_serial_tracked,
            is_batch_tracked=is_batch_tracked,
            is_expiration_tracked=is_expiration_tracked,
            temperature_requirements=temperature_requirements,
            created_by_id=user_id,
            updated_by_id=user_id,
        )
        self._s.add(product)
        await self._s.flush()

        # Базовая упаковка
        base_package = Package(
            product_id=product.id,
            name="шт",
            quantity=1,
            is_base_unit=True,
            created_by_id=user_id,
            updated_by_id=user_id,
        )
        self._s.add(base_package)
        await self._s.flush()

        logger.info("Товар создан: id=%s", product.id)
        return product

    async def get_by_id(self, product_id: int) -> Product | None:
        return await self._s.get(Product, product_id)

    async def get_by_external_id(self, depositor_id: int, external_id: str) -> Product | None:
        stmt = select(Product).where(
            Product.depositor_id == depositor_id,
            Product.external_id == external_id,
        )
        return await self._s.scalar(stmt)

    async def get_or_create(
        self,
        depositor_id: int,
        external_id: str,
        defaults: dict,
        user_id: int | None = None,
    ) -> tuple[Product, bool]:
        product = await self.get_by_external_id(depositor_id, external_id)
        if product:
            return product, False

        product = await self.create(
            depositor_id=depositor_id,
            external_id=external_id,
            name=defaults.get("name", external_id),
            sku=defaults.get("sku", external_id),
            group_id=defaults.get("group_id"),
            legal_name=defaults.get("legal_name", ""),
            weight=defaults.get("weight", Decimal("0")),
            volume=defaults.get("volume", Decimal("0")),
            price=defaults.get("price"),
            shelf_life_days=defaults.get("shelf_life_days"),
            min_shelf_life_days=defaults.get("min_shelf_life_days"),
            is_marked=defaults.get("is_marked", False),
            is_serial_tracked=defaults.get("is_serial_tracked", False),
            is_batch_tracked=defaults.get("is_batch_tracked", False),
            is_expiration_tracked=defaults.get("is_expiration_tracked", False),
            temperature_requirements=defaults.get("temperature_requirements", ""),
            user_id=user_id,
        )
        return product, True

    async def list_by_depositor(self, depositor_id: int) -> list[Product]:
        stmt = select(Product).where(
            Product.depositor_id == depositor_id,
        )
        return list(await self._s.scalars(stmt))

    async def soft_delete(self, product_id: int, user_id: int | None = None) -> bool:
        product = await self.get_by_id(product_id)
        if not product:
            return False
        product.soft_delete(user_id)
        await self._s.flush()
        return True
