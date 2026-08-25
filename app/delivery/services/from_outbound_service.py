"""Создание заявки на доставку из исходящего заказа."""

from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.statuses import DeliveryStatus
from app.delivery.models import DeliveryOrder
from app.delivery.repository import DeliveryOrderRepository
from app.delivery.services.delivery_order_service import DeliveryOrderService
from app.orders.repository import OutboundOrderRepository


class DeliveryFromOutboundService:
    """Идемпотентное создание DeliveryOrder по OutboundOrder с needs_delivery."""

    def __init__(
        self,
        delivery_orders: DeliveryOrderService,
        delivery_repo: DeliveryOrderRepository,
        outbound_repo: OutboundOrderRepository,
    ) -> None:
        self._delivery_orders = delivery_orders
        self._delivery_repo = delivery_repo
        self._outbound_repo = outbound_repo

    async def ensure_for_outbound(self, order_id: int) -> DeliveryOrder | None:
        outbound = await self._outbound_repo.get_by_id(order_id)
        if outbound is None or not outbound.needs_delivery:
            return None

        existing = await self._delivery_repo.get_by_outbound_order_id(order_id)
        if existing is not None:
            return existing

        contact = (outbound.delivery_contact or outbound.shipping_contact or "").strip()
        comment_parts = [
            p for p in (outbound.address_comment, outbound.notes) if p and p.strip()
        ]

        delivery = await self._delivery_orders.create(
            number=outbound.number,
            outbound_order_id=outbound.id,
            contact_person=contact,
            phone="",
            delivery_date=outbound.shipping_date or outbound.order_date,
            is_edo=outbound.is_edo,
            comment="; ".join(comment_parts),
            status=DeliveryStatus.CREATED.value,
        )

        await self._outbound_repo.update(
            outbound.id,
            delivery_status=DeliveryStatus.CREATED.value,
        )
        return delivery


def delivery_from_outbound_from_session(
    session: AsyncSession,
) -> DeliveryFromOutboundService:
    delivery_repo = DeliveryOrderRepository(session)
    return DeliveryFromOutboundService(
        delivery_orders=DeliveryOrderService(delivery_repo),
        delivery_repo=delivery_repo,
        outbound_repo=OutboundOrderRepository(session),
    )
