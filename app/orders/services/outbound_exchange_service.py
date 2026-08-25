"""Принятие заявки на отгрузку с обмена. Не UI-CRUD и не DataScope."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from decimal import Decimal

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import BadRequestError
from app.core.statuses import OrderStatus
from app.infrastructure.events import schedule_event
from app.infrastructure.events.event_types import EventTypes
from app.orders.exchange_messages import OutboundExchangeMessage
from app.orders.models import OutboundOrder
from app.orders.repository import OutboundOrderLineRepository, OutboundOrderRepository
from app.parties.repository import AddressRepository, ClientRepository, RawAddressRepository
from app.parties.services import AddressService, ClientService
from app.warehouse.repository import ProductRepository, VirtualWarehouseRepository
from app.warehouse.services import ProductService
from app.warehouse.services.topology_service import VirtualWarehouseService


@dataclass(frozen=True)
class OutboundExchangeAcceptResult:
    skipped: bool
    order: OutboundOrder | None


class OutboundExchangeService:
    def __init__(
        self,
        orders: OutboundOrderRepository,
        lines: OutboundOrderLineRepository,
        products: ProductService,
        clients: ClientService,
        addresses: AddressService,
        virtual_warehouses: VirtualWarehouseService,
    ) -> None:
        self._orders = orders
        self._lines = lines
        self._products = products
        self._clients = clients
        self._addresses = addresses
        self._vw = virtual_warehouses

    async def accept(
        self,
        *,
        depositor_id: int,
        message: OutboundExchangeMessage,
        user_id: int,
    ) -> OutboundExchangeAcceptResult:
        existing = await self._orders.get_by_depositor_number(
            depositor_id, message.number
        )
        if existing is not None:
            return OutboundExchangeAcceptResult(skipped=True, order=existing)

        resolved: list[tuple[int, Decimal]] = []
        for line in message.lines:
            product = await self._products.get_by_external_id(
                depositor_id, line.external_id
            )
            if product is None:
                raise BadRequestError(
                    f"Товар {line.external_id} не найден в справочнике — "
                    "исходящая заявка не создана"
                )
            resolved.append((product.id, line.quantity))

        address_text = message.delivery_address_raw.strip()
        if not address_text:
            raise BadRequestError("Пустой DELIV_ADDR — исходящая заявка не создана")

        try:
            address = await self._addresses.get_or_create(
                address_text, source="order_exchange"
            )
        except BadRequestError as e:
            raise BadRequestError(
                f"Адрес доставки: {e.detail} — исходящая заявка не создана"
            ) from e

        try:
            client, _ = await self._clients.get_or_create(
                user_id=user_id,
                depositor_id=depositor_id,
                code=message.customer.code,
                name=message.customer.name,
                legal_name=message.customer.legal_name,
                inn=message.customer.inn,
                kpp=message.customer.kpp,
                delivery_address_id=address.id,
                is_edo=message.customer.is_edo,
            )
        except BadRequestError as e:
            raise BadRequestError(
                f"Клиент {message.customer.code}: {e.detail} — "
                "исходящая заявка не создана"
            ) from e
        except Exception as e:
            raise BadRequestError(
                f"Клиент {message.customer.code}: не удалось создать — "
                "исходящая заявка не создана"
            ) from e

        loc_code = message.loc_code.strip()
        vw = await self._vw.get_by_depositor_code(depositor_id, loc_code)
        if vw is None:
            raise BadRequestError(
                f'Для LOC="{loc_code}" не найден виртуальный склад. '
                "Создайте его в топологии для этого поклажедателя."
            )

        order_date = message.document_date or message.delivery_date or date.today()
        total_qty = sum(int(qty) for _, qty in resolved)

        order = await self._orders.create(
            depositor_id=depositor_id,
            warehouse_id=vw.warehouse_id,
            number=message.number,
            client_id=client.id,
            customer_code=message.customer.code,
            customer_name=message.customer.name,
            delivery_address_name=message.consignee_name or address.full_address,
            order_date=order_date,
            shipping_date=message.delivery_date,
            needs_delivery=message.needs_delivery,
            delivery_only=False,
            delivery_contact=message.delivery_contact,
            shipping_contact=message.delivery_contact,
            address_comment=message.address_comment.strip(),
            is_edo=message.customer.is_edo,
            total_quantity=total_qty,
            status=OrderStatus.NEW.value,
            document_number=message.number,
        )

        for product_id, quantity in resolved:
            await self._lines.create(
                order_id=order.id,
                product_id=product_id,
                quantity=quantity,
            )

        schedule_event(
            self._orders._s,
            EventTypes.OUTBOUND_ORDER_ACCEPTED_FROM_EXCHANGE,
            {
                "order_id": order.id,
                "order_number": order.number,
                "depositor_id": depositor_id,
                "client_id": client.id,
                "needs_delivery": order.needs_delivery,
            },
        )
        return OutboundExchangeAcceptResult(skipped=False, order=order)


def outbound_exchange_from_session(session: AsyncSession) -> OutboundExchangeService:
    return OutboundExchangeService(
        orders=OutboundOrderRepository(session),
        lines=OutboundOrderLineRepository(session),
        products=ProductService(ProductRepository(session)),
        clients=ClientService(ClientRepository(session)),
        addresses=AddressService(
            AddressRepository(session), RawAddressRepository(session)
        ),
        virtual_warehouses=VirtualWarehouseService(
            VirtualWarehouseRepository(session)
        ),
    )
