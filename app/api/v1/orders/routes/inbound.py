"""API для входящих заказов."""

from __future__ import annotations

from fastapi import APIRouter, Depends, status

from app.api.deps import Services, UserDep, require_permission
from app.api.v1.orders.schemas import (
    InboundOrderCreate,
    InboundOrderLineCreate,
    InboundOrderLineRead,
    InboundOrderRead,
    InboundOrderUpdate,
)
from app.core.exceptions import NotFoundError
from app.orders.repository import InboundOrderLineRepository, InboundOrderRepository

router = APIRouter(prefix="/inbound-orders", tags=["inbound-orders"])


@router.get("", response_model=list[InboundOrderRead], dependencies=[Depends(require_permission("view", "orders"))])
async def list_inbound_orders(services: Services) -> list[InboundOrderRead]:
    from app.orders.repository import InboundOrderRepository
    rows = await InboundOrderRepository(services.session).list_all()
    return [InboundOrderRead.model_validate(r) for r in rows]


@router.post("", response_model=InboundOrderRead, status_code=status.HTTP_201_CREATED, dependencies=[Depends(require_permission("create", "orders"))])
async def create_inbound_order(body: InboundOrderCreate, services: Services, user_id: UserDep) -> InboundOrderRead:
    from app.orders.repository import InboundOrderRepository
    order = await InboundOrderRepository(services.session).create(**body.model_dump())
    return InboundOrderRead.model_validate(order)


@router.get("/{order_id}", response_model=InboundOrderRead, dependencies=[Depends(require_permission("view", "orders"))])
async def get_inbound_order(order_id: int, services: Services) -> InboundOrderRead:
    from app.orders.repository import InboundOrderRepository
    order = await InboundOrderRepository(services.session).get_by_id(order_id)
    if order is None:
        raise NotFoundError("Заявка не найдена")
    return InboundOrderRead.model_validate(order)


@router.patch("/{order_id}", response_model=InboundOrderRead, dependencies=[Depends(require_permission("update", "orders"))])
async def update_inbound_order(order_id: int, body: InboundOrderUpdate, services: Services, user_id: UserDep) -> InboundOrderRead:
    from app.orders.repository import InboundOrderRepository
    order = await InboundOrderRepository(services.session).update(order_id, **body.model_dump(exclude_unset=True))
    if order is None:
        raise NotFoundError("Заявка не найдена")
    return InboundOrderRead.model_validate(order)


@router.delete("/{order_id}", status_code=status.HTTP_204_NO_CONTENT, dependencies=[Depends(require_permission("delete", "orders"))])
async def delete_inbound_order(order_id: int, services: Services, user_id: UserDep) -> None:
    from app.orders.repository import InboundOrderRepository
    ok = await InboundOrderRepository(services.session).soft_delete(order_id, user_id)
    if not ok:
        raise NotFoundError("Заявка не найдена")


@router.get("/{order_id}/lines", response_model=list[InboundOrderLineRead], dependencies=[Depends(require_permission("view", "orders"))])
async def list_inbound_lines(order_id: int, services: Services) -> list[InboundOrderLineRead]:
    from app.orders.repository import InboundOrderLineRepository
    rows = await InboundOrderLineRepository(services.session).list_by_order(order_id)
    return [InboundOrderLineRead.model_validate(r) for r in rows]


@router.post("/{order_id}/lines", response_model=InboundOrderLineRead, status_code=status.HTTP_201_CREATED, dependencies=[Depends(require_permission("create", "orders"))])
async def create_inbound_line(order_id: int, body: InboundOrderLineCreate, services: Services, user_id: UserDep) -> InboundOrderLineRead:
    from app.orders.repository import InboundOrderLineRepository
    line = await InboundOrderLineRepository(services.session).create(order_id=order_id, **body.model_dump(exclude={"order_id"}))
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
