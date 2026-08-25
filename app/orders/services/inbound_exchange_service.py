"""Принятие заявки на приёмку с обмена. Не UI-CRUD и не DataScope."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import BadRequestError
from app.core.statuses import OrderStatus
from app.documents.repository import DocumentLineRepository, DocumentRepository
from app.documents.services.document_service import DocumentService
from app.infrastructure.events import schedule_event
from app.infrastructure.events.event_types import EventTypes
from app.orders.exchange_messages import InboundExchangeMessage
from app.orders.models import InboundOrder
from app.orders.repository import InboundOrderLineRepository, InboundOrderRepository
from app.parties.repository import ClientRepository
from app.parties.services import ClientService
from app.warehouse.repository import ProductRepository, VirtualWarehouseRepository
from app.warehouse.services import ProductService
from app.warehouse.services.topology_service import VirtualWarehouseService


@dataclass(frozen=True)
class InboundExchangeAcceptResult:
    skipped: bool
    order: InboundOrder | None


class InboundExchangeService:
    def __init__(
        self,
        orders: InboundOrderRepository,
        lines: InboundOrderLineRepository,
        products: ProductService,
        clients: ClientService,
        virtual_warehouses: VirtualWarehouseService,
        documents: DocumentService,
    ) -> None:
        self._orders = orders
        self._lines = lines
        self._products = products
        self._clients = clients
        self._vw = virtual_warehouses
        self._documents = documents

    async def accept(
        self,
        *,
        depositor_id: int,
        message: InboundExchangeMessage,
        user_id: int,
    ) -> InboundExchangeAcceptResult:
        existing = await self._orders.get_by_depositor_number(
            depositor_id, message.number
        )
        if existing is not None:
            return InboundExchangeAcceptResult(skipped=True, order=existing)

        for product in message.products:
            try:
                await self._products.get_or_create(
                    depositor_id=depositor_id,
                    external_id=product.external_id,
                    defaults={
                        "name": product.name or product.external_id,
                        "legal_name": product.legal_name,
                        "weight": product.net_mass,
                        "shelf_life_days": product.shelf_life_days,
                        "min_shelf_life_days": product.min_shelf_life_days,
                        "unit": product.unit or None,
                        "barcode": product.barcode or None,
                        "gross_mass": product.gross_mass,
                    },
                    user_id=user_id,
                )
            except ValueError as e:
                raise BadRequestError(f"Товар {product.external_id}: {e}") from e

        supplier, _ = await self._clients.get_or_create(
            user_id=user_id,
            depositor_id=depositor_id,
            code=message.vendor.code,
            name=message.vendor.name,
            legal_name=message.vendor.legal_name,
            inn=message.vendor.inn,
            kpp=message.vendor.kpp,
        )

        loc_code = message.loc_code.strip()
        vw = await self._vw.get_by_depositor_code(depositor_id, loc_code)
        if vw is None:
            raise BadRequestError(
                f'Для LOC="{loc_code}" не найден виртуальный склад. '
                "Создайте его в топологии для этого поклажедателя."
            )
        warehouse_id = vw.warehouse_id
        vw_id = vw.id

        order_date = message.document_date or message.delivery_date or date.today()

        order = await self._orders.create(
            depositor_id=depositor_id,
            warehouse_id=warehouse_id,
            number=message.number,
            order_number=message.order_number,
            loc_code=loc_code,
            supplier_code=message.vendor.code,
            supplier_id=supplier.id,
            order_date=order_date,
            planned_date=message.delivery_date,
        )

        for line in message.lines:
            product = await self._products.get_by_external_id(
                depositor_id, line.external_id
            )
            if product is None:
                raise BadRequestError(
                    f"Товар {line.external_id} не найден после загрузки справочника"
                )
            await self._lines.create(
                order_id=order.id,
                product_id=product.id,
                quantity=line.quantity,
            )

        document = await self._documents.create(
            user_id=user_id,
            document_type="receipt",
            warehouse_id=warehouse_id,
            virtual_warehouse_id=vw_id,
            inbound_order_id=order.id,
            document_number=message.number,
            document_date=message.document_date or order_date,
            delivery_date=message.delivery_date,
            status="draft",
        )
        for line in message.lines:
            product = await self._products.get_by_external_id(
                depositor_id, line.external_id
            )
            if product is None:
                raise BadRequestError(
                    f"Товар {line.external_id} не найден после загрузки справочника"
                )
            await self._documents.add_line(
                user_id=user_id,
                document_id=document.id,
                product_id=product.id,
                quantity=line.quantity,
            )

        await self._orders.update(order.id, status=OrderStatus.DOCUMENT_CREATED.value)

        schedule_event(
            self._orders._s,
            EventTypes.INBOUND_ORDER_ACCEPTED_FROM_EXCHANGE,
            {
                "order_id": order.id,
                "order_number": order.number,
                "depositor_id": depositor_id,
            },
        )
        return InboundExchangeAcceptResult(skipped=False, order=order)


def inbound_exchange_from_session(session: AsyncSession) -> InboundExchangeService:
    return InboundExchangeService(
        orders=InboundOrderRepository(session),
        lines=InboundOrderLineRepository(session),
        products=ProductService(ProductRepository(session)),
        clients=ClientService(ClientRepository(session)),
        virtual_warehouses=VirtualWarehouseService(
            VirtualWarehouseRepository(session)
        ),
        documents=DocumentService(
            DocumentRepository(session), DocumentLineRepository(session)
        ),
    )
