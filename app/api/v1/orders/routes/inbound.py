"""API для входящих заказов."""

from __future__ import annotations

from fastapi import APIRouter, Depends, status

from app.api.deps import ScopeDep, Services, UserDep, require_permission
from app.api.v1.orders.schemas import (
    InboundOrderCreate,
    InboundOrderLineCreate,
    InboundOrderLineRead,
    InboundOrderRead,
    InboundOrderUpdate,
)
from app.core.exceptions import NotFoundError

router = APIRouter(prefix="/inbound-orders", tags=["inbound-orders"])


@router.get("", response_model=list[InboundOrderRead], dependencies=[Depends(require_permission("view", "orders"))])
async def list_inbound_orders(services: Services, scope: ScopeDep) -> list[InboundOrderRead]:
    rows = await services.inbound_order.list_all(scope)
    return [InboundOrderRead.model_validate(r) for r in rows]


@router.post("", response_model=InboundOrderRead, status_code=status.HTTP_201_CREATED, dependencies=[Depends(require_permission("create", "orders"))])
async def create_inbound_order(body: InboundOrderCreate, services: Services, scope: ScopeDep) -> InboundOrderRead:
    order = await services.inbound_order.create(scope=scope, **body.model_dump())
    return InboundOrderRead.model_validate(order)


@router.get("/{order_id}", response_model=InboundOrderRead, dependencies=[Depends(require_permission("view", "orders"))])
async def get_inbound_order(order_id: int, services: Services, scope: ScopeDep) -> InboundOrderRead:
    order = await services.inbound_order.get_by_id(order_id, scope)
    if order is None:
        raise NotFoundError("Заявка не найдена")
    return InboundOrderRead.model_validate(order)


@router.patch("/{order_id}", response_model=InboundOrderRead, dependencies=[Depends(require_permission("update", "orders"))])
async def update_inbound_order(order_id: int, body: InboundOrderUpdate, services: Services, scope: ScopeDep) -> InboundOrderRead:
    order = await services.inbound_order.update(order_id, scope, **body.model_dump(exclude_unset=True))
    if order is None:
        raise NotFoundError("Заявка не найдена")
    return InboundOrderRead.model_validate(order)


@router.delete("/{order_id}", status_code=status.HTTP_204_NO_CONTENT, dependencies=[Depends(require_permission("delete", "orders"))])
async def delete_inbound_order(order_id: int, services: Services, user_id: UserDep, scope: ScopeDep) -> None:
    ok = await services.inbound_order.soft_delete(order_id, user_id, scope)
    if not ok:
        raise NotFoundError("Заявка не найдена")


@router.get("/{order_id}/lines", response_model=list[InboundOrderLineRead], dependencies=[Depends(require_permission("view", "orders"))])
async def list_inbound_lines(order_id: int, services: Services, scope: ScopeDep) -> list[InboundOrderLineRead]:
    order = await services.inbound_order.get_by_id(order_id, scope)
    if order is None:
        raise NotFoundError("Заявка не найдена")
    rows = await services.inbound_order.list_lines(order_id)
    return [InboundOrderLineRead.model_validate(r) for r in rows]


@router.post("/{order_id}/lines", response_model=InboundOrderLineRead, status_code=status.HTTP_201_CREATED, dependencies=[Depends(require_permission("create", "orders"))])
async def create_inbound_line(order_id: int, body: InboundOrderLineCreate, services: Services, scope: ScopeDep, user_id: UserDep) -> InboundOrderLineRead:
    order = await services.inbound_order.get_by_id(order_id, scope)
    if order is None:
        raise NotFoundError("Заявка не найдена")
    line = await services.inbound_order.add_line(user_id=user_id, order_id=order_id, **body.model_dump(exclude={"order_id"}))
    return InboundOrderLineRead.model_validate(line)


@router.patch("/lines/{line_id}", response_model=InboundOrderLineRead, dependencies=[Depends(require_permission("update", "orders"))])
async def update_inbound_line(line_id: int, body: InboundOrderLineCreate, services: Services, user_id: UserDep) -> InboundOrderLineRead:
    from app.orders.repository import InboundOrderLineRepository
    line = await InboundOrderLineRepository(services.session).update(line_id, **body.model_dump(exclude_unset=True, exclude={"order_id"}))
    if line is None:
        raise NotFoundError("Строка не найдена")
    return InboundOrderLineRead.model_validate(line)


@router.delete("/lines/{line_id}", status_code=status.HTTP_204_NO_CONTENT, dependencies=[Depends(require_permission("delete", "orders"))])
async def delete_inbound_line(line_id: int, services: Services, user_id: UserDep) -> None:
    from app.orders.repository import InboundOrderLineRepository
    ok = await InboundOrderLineRepository(services.session).soft_delete(line_id, user_id)
    if not ok:
        raise NotFoundError("Строка не найдена")
