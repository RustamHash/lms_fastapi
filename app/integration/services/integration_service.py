"""Сервис импорта заказов."""

from __future__ import annotations

import logging
from datetime import date
from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.orders.models import (
    InboundOrder,
    InboundOrderLine,
    OutboundOrder,
    OutboundOrderLine,
)
from app.delivery.models import DeliveryOrder
from app.delivery.repository import DeliveryOrderRepository
from app.delivery.services import DeliveryOrderService
from app.documents.services.document_service import DocumentService
from app.documents.repository import DocumentLineRepository, DocumentRepository
from app.integration.adapters import ZLNAdapter
from app.parties.models import Client
from app.warehouse.models import VirtualWarehouse
from app.parties.services import AddressService, ClientService
from app.parties.repository import AddressRepository, ClientRepository, RawAddressRepository
from app.warehouse.repository import ProductRepository
from app.warehouse.services import ProductService

logger = logging.getLogger(__name__)


class IntegrationService:
    """Обработка импортированных документов."""

    def __init__(self, session: AsyncSession) -> None:
        self._s = session

    async def process_document(
        self,
        universal_doc: dict,
        depositor_id: int,
        user_id: int,
    ) -> tuple[object | None, list[str], bool]:
        """Вернуть (заказ, ошибки, skipped). skipped=True — дубликат, не ошибка."""
        errors: list[str] = []
        savepoint = None

        logger.info("Начало импорта: %s", universal_doc.get("document_number"))
        doc_type = universal_doc.get("document_type")
        doc_number = universal_doc.get("document_number", "")

        try:
            try:
                savepoint = await self._s.begin_nested()
            except Exception as e:
                logger.error("Не удалось начать транзакцию: %s", e)
                return None, [f"Ошибка транзакции: {e}"], False

            if doc_type == "porder":
                existing = await self._s.scalar(
                    select(InboundOrder).where(
                        InboundOrder.depositor_id == depositor_id,
                        InboundOrder.number == doc_number,
                    )
                )
            elif doc_type == "order":
                existing = await self._s.scalar(
                    select(OutboundOrder).where(
                        OutboundOrder.depositor_id == depositor_id,
                        OutboundOrder.number == doc_number,
                    )
                )
            else:
                existing = None

            if existing:
                logger.info("Заказ %s уже существует, пропускаю", doc_number)
                await self._rollback_savepoint(savepoint)
                return None, [], True

            product_service = ProductService(ProductRepository(self._s))
            for item in universal_doc.get("items", []):
                try:
                    await product_service.get_or_create(
                        depositor_id=depositor_id,
                        external_id=item["external_id"],
                        defaults={
                            "name": item.get("name", item["external_id"]),
                            "legal_name": item.get("legal_name", ""),
                            "weight": item.get("net_mass", 0),
                            "shelf_life_days": item.get("shelf_life_days"),
                            "min_shelf_life_days": item.get("min_shelf_life_days"),
                            "unit": item.get("unit"),
                            "barcode": item.get("ean"),
                            "gross_mass": item.get("gross_mass"),
                        },
                        user_id=user_id,
                    )
                except ValueError as e:
                    errors.append(f"Товар {item['external_id']}: {e}")

            if errors:
                await self._rollback_savepoint(savepoint)
                return None, errors, False

            if doc_type == "porder":
                order = await self._create_inbound_order(
                    universal_doc, depositor_id, user_id
                )
            elif doc_type == "order":
                order = await self._create_outbound_order(
                    universal_doc, depositor_id, user_id
                )
            else:
                await self._rollback_savepoint(savepoint)
                return None, [f"Неизвестный тип документа: {doc_type}"], False

            await self._commit_savepoint(savepoint)
            logger.info("Импорт завершён: %s", universal_doc.get("document_number"))
            return order, [], False

        except Exception as e:
            await self._rollback_savepoint(savepoint)
            logger.error("Ошибка импорта: %s", e, exc_info=True)
            return None, [f"Ошибка: {e}"], False

    async def _rollback_savepoint(self, savepoint) -> None:
        if savepoint is None:
            return
        try:
            await savepoint.rollback()
        except Exception as rollback_error:
            logger.error(
                "Ошибка отката транзакции: %s", rollback_error, exc_info=True
            )

    async def _commit_savepoint(self, savepoint) -> None:
        if savepoint is None:
            return
        try:
            await savepoint.commit()
        except Exception as commit_error:
            logger.error("Ошибка фиксации savepoint: %s", commit_error, exc_info=True)
            raise

    async def _lookup_virtual_warehouse(
        self, depositor_id: int, vw_code: str
    ) -> tuple[int | None, int | None]:
        """Найти существующий VW по коду LOC. Пустой код — (None, None). Нет VW — ошибка."""
        code = (vw_code or "").strip()
        if not code:
            return None, None

        vw = await self._s.scalar(
            select(VirtualWarehouse).where(
                VirtualWarehouse.depositor_id == depositor_id,
                VirtualWarehouse.code == code,
            )
        )
        if vw is None:
            raise ValueError(
                f'Для LOC="{code}" не найден виртуальный склад. '
                "Создайте его в топологии для этого поклажедателя."
            )
        return vw.warehouse_id, vw.id

    async def _get_or_create_warehouse(
        self, depositor_id: int, vw_code: str, user_id: int | None = None
    ) -> tuple[int, int | None]:
        """Найти или создать виртуальный склад, вернуть (warehouse_id, vw_id)."""
        from app.warehouse.models import Warehouse

        if vw_code:
            # Ищем виртуальный склад
            stmt = select(VirtualWarehouse).where(
                VirtualWarehouse.depositor_id == depositor_id,
                VirtualWarehouse.code == vw_code,
            )
            vw = await self._s.scalar(stmt)
            if vw:
                return vw.warehouse_id, vw.id

            # Не нашли — создаем
            warehouse = await self._s.scalar(select(Warehouse).limit(1))
            if warehouse is None:
                raise ValueError("Склад не найден")

            vw = VirtualWarehouse(
                depositor_id=depositor_id,
                warehouse_id=warehouse.id,
                code=vw_code,
                name=vw_code,
                created_by_id=user_id,
                updated_by_id=user_id,
            )
            self._s.add(vw)
            await self._s.flush()
            return vw.warehouse_id, vw.id

        # Без кода — ошибка, заказ не создаем
        raise ValueError("Виртуальный склад не указан (LOC)")

    async def _create_inbound_order(
        self,
        doc: dict,
        depositor_id: int,
        user_id: int,
    ) -> InboundOrder:
        """Создать входящий заказ (приёмка)."""
        # 1. Проверить дубликат
        existing = await self._s.scalar(
            select(InboundOrder).where(
                InboundOrder.depositor_id == depositor_id,
                InboundOrder.number == doc["document_number"],
            )
        )
        if existing:
            raise ValueError(f"Заказ {doc['document_number']} уже существует")

        # 2. Найти/создать поставщика (Client без адреса)
        client_service = ClientService(ClientRepository(self._s))
        vendor_code = doc.get("vendor_code", "")
        if vendor_code:
            supplier, _ = await client_service.get_or_create(
                user_id=user_id,
                depositor_id=depositor_id,
                code=vendor_code,
                name=doc.get("vendor_name", vendor_code),
                legal_name=doc.get("vendor_legal_name", ""),
                inn=doc.get("vendor_inn", ""),
                kpp=doc.get("vendor_kpp", ""),
            )
        else:
            supplier = None

        loc_code = (doc.get("virtual_warehouse_code") or "").strip()
        warehouse_id, vw_id = await self._lookup_virtual_warehouse(
            depositor_id, loc_code
        )

        order_date = doc.get("document_date") or doc.get("delivery_date") or date.today()
        notes = f"LOC: {loc_code}" if loc_code else "LOC: "

        order = InboundOrder(
            depositor_id=depositor_id,
            warehouse_id=warehouse_id,
            number=doc["document_number"],
            supplier_code=vendor_code,
            supplier_id=supplier.id if supplier else None,
            order_date=order_date,
            planned_date=doc.get("delivery_date"),
            notes=notes,
        )
        self._s.add(order)
        await self._s.flush()

        # 5. Создать строки
        for line in doc.get("lines", []):
            from app.warehouse.models import Product

            stmt = select(Product).where(
                Product.depositor_id == depositor_id,
                Product.external_id == line["external_id"],
            )
            product = await self._s.scalar(stmt)

            if product is None:
                continue

            order_line = InboundOrderLine(
                order_id=order.id,
                product_id=product.id,
                quantity=line["quantity"],
            )
            self._s.add(order_line)

        await self._s.flush()

        if warehouse_id is None:
            return order

        doc_service = DocumentService(
            DocumentRepository(self._s), DocumentLineRepository(self._s)
        )
        document = await doc_service.create(
            user_id=user_id,
            document_type="receipt",
            warehouse_id=warehouse_id,
            virtual_warehouse_id=vw_id,
            inbound_order_id=order.id,
            document_number=doc["document_number"],
            document_date=doc.get("document_date") or order_date,
            delivery_date=doc.get("delivery_date"),
            status="draft",
        )

        for line in doc.get("lines", []):
            from app.warehouse.models import Product

            stmt = select(Product).where(
                Product.depositor_id == depositor_id,
                Product.external_id == line["external_id"],
            )
            product = await self._s.scalar(stmt)
            if product:
                await doc_service.add_line(
                    user_id=user_id,
                    document_id=document.id,
                    product_id=product.id,
                    quantity=line["quantity"],
                )

        order.status = "document_created"
        await self._s.flush()

        return order

    async def _create_outbound_order(
        self,
        doc: dict,
        depositor_id: int,
        user_id: int,
    ) -> OutboundOrder:
        """Создать исходящий заказ (отгрузка)."""
        customer_code = doc.get("customer_code", "")
        delivery_address = doc.get("delivery_address", "")

        # 1. Проверить дубликат
        existing = await self._s.scalar(
            select(OutboundOrder).where(
                OutboundOrder.depositor_id == depositor_id,
                OutboundOrder.number == doc["document_number"],
            )
        )
        if existing:
            raise ValueError(f"Заказ {doc['document_number']} уже существует")

        # 2. Найти/создать адрес доставки
        address_service = AddressService(
            AddressRepository(self._s),
            RawAddressRepository(self._s),
        )
        address = await address_service.get_or_create(
            delivery_address, "import", user_id
        )

        # 3. Найти/создать клиента (code + delivery_address_id)
        client_service = ClientService(ClientRepository(self._s))
        client, _ = await client_service.get_or_create(
            user_id=user_id,
            depositor_id=depositor_id,
            code=customer_code,
            name=doc.get("customer_name", customer_code),
            legal_name=doc.get("customer_legal_name", ""),
            inn=doc.get("customer_inn", ""),
            kpp=doc.get("customer_kpp", ""),
            delivery_address_id=address.id,
            is_edo=doc.get("use_edo", False),
        )

        # 4. Найти склад
        warehouse_id, vw_id = await self._get_or_create_warehouse(
            depositor_id, doc.get("virtual_warehouse_code", ""), user_id
        )

        # 5. Создать заказ
        # Рассчитать вес и количество
        total_weight = Decimal("0")
        total_qty = 0
        for line in doc.get("lines", []):
            total_qty += line["quantity"]
            for item in doc.get("items", []):
                if item["external_id"] == line["external_id"]:
                    total_weight += item["net_mass"] * line["quantity"]
                    break

        order = OutboundOrder(
            depositor_id=depositor_id,
            warehouse_id=warehouse_id,
            number=doc["document_number"],
            customer_code=customer_code,
            customer_name=client.name,
            delivery_address_name=delivery_address,
            client_id=client.id,
            order_date=doc.get("document_date") or doc.get("delivery_date"),
            shipping_date=doc.get("delivery_date"),
            needs_delivery=doc.get("is_delivery", False),
            declared_weight=total_weight,
            address_comment=doc.get("address_comment", ""),
            shipping_contact=doc.get("shipping_contact", ""),
            total_quantity=total_qty,
        )
        self._s.add(order)
        await self._s.flush()

        # 6. Создать строки
        for line in doc.get("lines", []):
            from app.warehouse.models import Product

            stmt = select(Product).where(
                Product.depositor_id == depositor_id,
                Product.external_id == line["external_id"],
            )
            product = await self._s.scalar(stmt)

            if product is None:
                continue

            order_line = OutboundOrderLine(
                order_id=order.id,
                product_id=product.id,
                quantity=line["quantity"],
            )
            self._s.add(order_line)

        await self._s.flush()

        # 7. Создать складской документ (shipment)
        doc_service = DocumentService(
            DocumentRepository(self._s), DocumentLineRepository(self._s)
        )
        document = await doc_service.create(
            user_id=user_id,
            document_type="shipment",
            warehouse_id=warehouse_id,
            document_number=doc["document_number"],
            document_date=doc.get("document_date"),
            delivery_date=doc.get("delivery_date"),
            status="draft",
        )

        # Строки документа
        for line in doc.get("lines", []):
            from app.warehouse.models import Product

            stmt = select(Product).where(
                Product.depositor_id == depositor_id,
                Product.external_id == line["external_id"],
            )
            product = await self._s.scalar(stmt)
            if product:
                await doc_service.add_line(
                    user_id=user_id,
                    document_id=document.id,
                    product_id=product.id,
                    quantity=line["quantity"],
                )

        # 8. Если нужна доставка — создать заявку через сервис
        if order.needs_delivery:
            delivery_service = DeliveryOrderService(DeliveryOrderRepository(self._s))
            await delivery_service.create(
                user_id=user_id,
                number=order.number,
                contract_id=None,
                document_id=document.id,
                outbound_order_id=order.id,
                contact_person=order.delivery_contact or "",
                phone="",
                delivery_date=order.shipping_date,
                status="created",
                is_edo=False,
                comment="",
            )

        # Обновить статус заказа
        order.status = "document_created"
        await self._s.flush()

        return order


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
