"""Портал поклажедателя: read-only API под /api/v1/portal."""

from __future__ import annotations

from fastapi import APIRouter, Depends

from app.api.deps import PortalUser, ScopeDep, SessionDep
from app.api.v1.orders.schemas.inbound import InboundOrderRead
from app.api.v1.orders.schemas.outbound import OutboundOrderRead
from app.api.v1.parties.schemas import DepositorRead
from app.api.v1.warehouse.schemas import ProductRead
from app.core.exceptions import ForbiddenError, NotFoundError
from app.orders.repository import InboundOrderRepository, OutboundOrderRepository
from app.parties.repository import DepositorRepository
from app.warehouse.repository import ProductRepository, StockRepository

router = APIRouter(prefix="/portal", tags=["portal"])


def _require_depositor(scope: ScopeDep) -> int:
    depositor_id = scope.single_depositor_id
    if depositor_id is None:
        # Несколько привязок — берём первый (портал обычно 1:1)
        if not scope.depositor_ids:
            raise ForbiddenError("Пользователь портала не привязан к поклажедателю")
        return sorted(scope.depositor_ids)[0]
    return depositor_id


@router.get("/me")
async def portal_me(user: PortalUser, scope: ScopeDep, session: SessionDep) -> dict:
    depositor_id = _require_depositor(scope)
    depositor = await DepositorRepository(session).get_by_id(depositor_id, scope=scope)
    if depositor is None:
        raise NotFoundError("Поклажедатель не найден")
    return {
        "user_id": user.id,
        "username": user.username,
        "is_portal_user": True,
        "depositor": DepositorRead.model_validate(depositor),
    }


@router.get("/dashboard")
async def portal_dashboard(
    user: PortalUser, scope: ScopeDep, session: SessionDep
) -> dict:
    depositor_id = _require_depositor(scope)
    inbound = await InboundOrderRepository(session).list_all(scope=scope)
    outbound = await OutboundOrderRepository(session).list_all(scope=scope)
    products = await ProductRepository(session).list_by_depositor(
        depositor_id, scope=scope
    )
    return {
        "depositor_id": depositor_id,
        "inbound_orders": len(inbound),
        "outbound_orders": len(outbound),
        "products": len(products),
    }


@router.get("/products", response_model=list[ProductRead])
async def portal_products(
    user: PortalUser, scope: ScopeDep, session: SessionDep
) -> list[ProductRead]:
    depositor_id = _require_depositor(scope)
    rows = await ProductRepository(session).list_by_depositor(depositor_id, scope=scope)
    return [ProductRead.model_validate(r) for r in rows]


@router.get("/orders/inbound", response_model=list[InboundOrderRead])
async def portal_inbound(
    user: PortalUser, scope: ScopeDep, session: SessionDep
) -> list[InboundOrderRead]:
    rows = await InboundOrderRepository(session).list_all(scope=scope)
    return [InboundOrderRead.model_validate(r) for r in rows]


@router.get("/orders/outbound", response_model=list[OutboundOrderRead])
async def portal_outbound(
    user: PortalUser, scope: ScopeDep, session: SessionDep
) -> list[OutboundOrderRead]:
    rows = await OutboundOrderRepository(session).list_all(scope=scope)
    return [OutboundOrderRead.model_validate(r) for r in rows]


@router.get("/stock")
async def portal_stock(
    user: PortalUser, scope: ScopeDep, session: SessionDep
) -> list[dict]:
    """Остатки товаров своего поклажедателя."""
    depositor_id = _require_depositor(scope)
    products = {
        p.id: p
        for p in await ProductRepository(session).list_by_depositor(
            depositor_id, scope=scope
        )
    }
    balances = await StockRepository(session).list_by_depositor(depositor_id)
    result: list[dict] = []
    for b in balances:
        product = products.get(b.product_id)
        result.append(
            {
                "product_id": b.product_id,
                "sku": product.sku if product else None,
                "name": product.name if product else None,
                "location_id": b.location_id,
                "quantity": str(b.quantity),
                "reserved_quantity": str(b.reserved_quantity),
            }
        )
    return result
