"""API для исходящих заказов."""

from __future__ import annotations

from fastapi import APIRouter, Depends, status

from app.api.deps import ScopeDep, Services, UserDep, require_permission
from app.api.v1.orders.schemas import (
    OutboundOrderCreate,
    OutboundOrderLineCreate,
    OutboundOrderLineRead,
    OutboundOrderRead,
    OutboundOrderUpdate,
)
from app.core.exceptions import NotFoundError

router = APIRouter(prefix="/outbound-orders", tags=["outbound-orders"])


@router.get("", response_model=list[OutboundOrderRead], dependencies=[Depends(require_permission("view", "orders"))])
async def list_outbound_orders(services: Services, scope: ScopeDep) -> list[OutboundOrderRead]:
    rows = await services.outbound_order.list_all(scope)
    return [OutboundOrderRead.model_validate(r) for r in rows]


@router.post("", response_model=OutboundOrderRead, status_code=status.HTTP_201_CREATED, dependencies=[Depends(require_permission("create", "orders"))])
async def create_outbound_order(body: OutboundOrderCreate, services: Services, scope: ScopeDep) -> OutboundOrderRead:
    order = await services.outbound_order.create(scope=scope, **body.model_dump())
    return OutboundOrderRead.model_validate(order)


@router.get("/{order_id}", response_model=OutboundOrderRead, dependencies=[Depends(require_permission("view", "orders"))])
async def get_outbound_order(order_id: int, services: Services, scope: ScopeDep) -> OutboundOrderRead:
    order = await services.outbound_order.get_by_id(order_id, scope)
    if order is None:
        raise NotFoundError("Заявка не найдена")
    return OutboundOrderRead.model_validate(order)


@router.patch("/{order_id}", response_model=OutboundOrderRead, dependencies=[Depends(require_permission("update", "orders"))])
async def update_outbound_order(order_id: int, body: OutboundOrderUpdate, services: Services, scope: ScopeDep) -> OutboundOrderRead:
    order = await services.outbound_order.update(order_id, scope, **body.model_dump(exclude_unset=True))
    if order is None:
        raise NotFoundError("Заявка не найдена")
    return OutboundOrderRead.model_validate(order)


@router.delete("/{order_id}", status_code=status.HTTP_204_NO_CONTENT, dependencies=[Depends(require_permission("delete", "orders"))])
async def delete_outbound_order(order_id: int, services: Services, current_user_id: UserDep, scope: ScopeDep) -> None:
    ok = await services.outbound_order.soft_delete(order_id, current_user_id, scope)
    if not ok:
        raise NotFoundError("Заявка не найдена")


@router.get("/{order_id}/lines", response_model=list[OutboundOrderLineRead], dependencies=[Depends(require_permission("view", "orders"))])
async def list_outbound_lines(order_id: int, services: Services, scope: ScopeDep) -> list[OutboundOrderLineRead]:
    order = await services.outbound_order.get_by_id(order_id, scope)
    if order is None:
        raise NotFoundError("Заявка не найдена")
    rows = await services.outbound_order.list_lines(order_id)
    return [OutboundOrderLineRead.model_validate(r) for r in rows]


@router.post("/{order_id}/lines", response_model=OutboundOrderLineRead, status_code=status.HTTP_201_CREATED, dependencies=[Depends(require_permission("create", "orders"))])
async def create_outbound_line(order_id: int, body: OutboundOrderLineCreate, services: Services, scope: ScopeDep, user_id: UserDep) -> OutboundOrderLineRead:
    order = await services.outbound_order.get_by_id(order_id, scope)
    if order is None:
        raise NotFoundError("Заявка не найдена")
    line = await services.outbound_order.add_line(user_id=user_id, order_id=order_id, **body.model_dump(exclude={"order_id"}))
    return OutboundOrderLineRead.model_validate(line)


@router.patch("/lines/{line_id}", response_model=OutboundOrderLineRead, dependencies=[Depends(require_permission("update", "orders"))])
async def update_outbound_line(line_id: int, body: OutboundOrderLineCreate, services: Services, user_id: UserDep) -> OutboundOrderLineRead:
    line = await services.outbound_order.update_line(line_id, user_id, **body.model_dump(exclude_unset=True, exclude={"order_id"}))
    if line is None:
        raise NotFoundError("Строка не найдена")
    return OutboundOrderLineRead.model_validate(line)


@router.delete("/lines/{line_id}", status_code=status.HTTP_204_NO_CONTENT, dependencies=[Depends(require_permission("delete", "orders"))])
async def delete_outbound_line(line_id: int, services: Services, user_id: UserDep) -> None:
    ok = await services.outbound_order.delete_line(line_id, user_id)
    if not ok:
        raise NotFoundError("Строка не найдена")
