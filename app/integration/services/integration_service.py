"""Сервис импорта заказов."""

from __future__ import annotations

import logging

from sqlalchemy.ext.asyncio import AsyncSession

logger = logging.getLogger(__name__)

from app.documents.models import Document, DocumentLine
from app.integration.adapters import ZLNAdapter
from app.parties.services import AddressService, ClientService, TradePointService
from app.parties.repository import AddressRepository, ClientRepository, TradePointRepository
from app.warehouse.services import ProductService, BatchService


class IntegrationService:
    """Обработка импортированных документов."""

    def __init__(self, session: AsyncSession) -> None:
        self._s = session

    async def process_document(
        self,
        universal_doc: dict,
        depositor_id: int,
        user_id: int,
    ) -> tuple[Document | None, list[str]]:
        errors = []

        logger.info("Начало импорта документа: %s", universal_doc.get("document_number"))
        try:
            # 1. Создаём товары
            product_service = ProductService(self._s)
            for item in universal_doc.get("items", []):
                try:
                    await product_service.get_or_create(
                        depositor_id=depositor_id,
                        external_id=item["external_id"],
                        defaults={
                            "name": item.get("name", item["external_id"]),
                            "weight": item.get("weight", 0),
                            "shelf_life_days": item.get("shelf_life_days"),
                        },
                        user_id=user_id,
                    )
                except ValueError as e:
                    errors.append(f"Товар {item['external_id']}: {e}")

            # 2. Создаём документ
            if errors:
                return None, errors

            from app.documents.services import DocumentService
            doc_service = DocumentService(self._s)

            # Определяем склад
            from app.warehouse.models import VirtualWarehouse
            from sqlalchemy import select

            vw = None
            vw_code = universal_doc.get("virtual_warehouse_code")
            if vw_code:
                stmt = select(VirtualWarehouse).where(
                    VirtualWarehouse.depositor_id == depositor_id,
                    VirtualWarehouse.code == vw_code,
                )
                vw = await self._s.scalar(stmt)

            if vw is None:
                # Берём первый склад
                from app.warehouse.models import Warehouse
                stmt = select(Warehouse).limit(1)
                warehouse = await self._s.scalar(stmt)
                if warehouse is None:
                    return None, ["Склад не найден"]
                warehouse_id = warehouse.id
            else:
                warehouse_id = vw.warehouse_id

            document = await doc_service.create(
                user_id=user_id,
                document_type=universal_doc["document_type"],
                warehouse_id=warehouse_id,
                document_number=universal_doc["document_number"],
                document_date=universal_doc.get("document_date"),
                delivery_date=universal_doc.get("delivery_date"),
                virtual_warehouse_id=vw.id if vw else None,
                is_delivery=universal_doc.get("is_delivery", False),
            )

            # 3. Создаём строки
            for line in universal_doc.get("lines", []):
                from sqlalchemy import select
                from app.warehouse.models import Product

                stmt = select(Product).where(
                    Product.depositor_id == depositor_id,
                    Product.external_id == line["external_id"],
                )
                product = await self._s.scalar(stmt)

                if product is None:
                    errors.append(f"Товар {line['external_id']} не найден")
                    continue

                await doc_service.add_line(
                    user_id=user_id,
                    document_id=document.id,
                    product_id=product.id,
                    quantity=line["quantity"],
                )

            if errors:
                return None, errors

            logger.info("Импорт завершён: %s", universal_doc.get("document_number"))
            return document, []

        except Exception as e:
            return None, [f"Ошибка: {e}"]


class AdapterService:
    """Выбор адаптера."""

    ADAPTERS = {
        "ZLN": ZLNAdapter,
    }

    @classmethod
    def get_adapter(cls, partner_code: str):
        adapter = cls.ADAPTERS.get(partner_code)
        if not adapter:
            raise ValueError(f"Адаптер для {partner_code} не найден")
        return adapter()
