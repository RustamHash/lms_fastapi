"""API для входящих заказов."""

from __future__ import annotations

from fastapi import APIRouter, Depends, status
from sqlalchemy import select

from app.api.deps import SessionDep, UserDep, require_permission
from app.api.v1.orders.schemas import (
    InboundOrderCreate,
    InboundOrderLineCreate,
    InboundOrderLineRead,
    InboundOrderRead,
    InboundOrderUpdate,
)
from app.core.exceptions import NotFoundError
from app.orders.models import InboundOrder, InboundOrderLine

router = APIRouter(prefix="/inbound-orders", tags=["inbound-orders"])


@router.get("", response_model=list[InboundOrderRead], dependencies=[Depends(require_permission("view", "orders"))])
async def list_inbound_orders(session: SessionDep) -> list[InboundOrderRead]:
    rows = list(await session.scalars(select(InboundOrder)))
    return [InboundOrderRead.model_validate(r) for r in rows]


@router.post("", response_model=InboundOrderRead, status_code=status.HTTP_201_CREATED, dependencies=[Depends(require_permission("create", "orders"))])
async def create_inbound_order(body: InboundOrderCreate, session: SessionDep, user_id: UserDep) -> InboundOrderRead:
    order = InboundOrder(created_by_id=user_id, updated_by_id=user_id, **body.model_dump())
    session.add(order)
    await session.flush()
    return InboundOrderRead.model_validate(order)


@router.get("/{order_id}", response_model=InboundOrderRead, dependencies=[Depends(require_permission("view", "orders"))])
async def get_inbound_order(order_id: int, session: SessionDep) -> InboundOrderRead:
    order = await session.get(InboundOrder, order_id)
    if order is None:
        raise NotFoundError("Заявка не найдена")
    return InboundOrderRead.model_validate(order)


@router.patch("/{order_id}", response_model=InboundOrderRead, dependencies=[Depends(require_permission("update", "orders"))])
async def update_inbound_order(order_id: int, body: InboundOrderUpdate, session: SessionDep, user_id: UserDep) -> InboundOrderRead:
    order = await session.get(InboundOrder, order_id)
    if order is None:
        raise NotFoundError("Заявка не найдена")
    for field, value in body.model_dump(exclude_unset=True).items():
        setattr(order, field, value)
    order.updated_by_id = user_id
    await session.flush()
    return InboundOrderRead.model_validate(order)


@router.delete("/{order_id}", status_code=status.HTTP_204_NO_CONTENT, dependencies=[Depends(require_permission("delete", "orders"))])
async def delete_inbound_order(order_id: int, session: SessionDep, user_id: UserDep) -> None:
    order = await session.get(InboundOrder, order_id)
    if order is None:
        raise NotFoundError("Заявка не найдена")
    order.soft_delete(user_id)
    await session.flush()


# ========== Строки ==========

@router.get("/{order_id}/lines", response_model=list[InboundOrderLineRead], dependencies=[Depends(require_permission("view", "orders"))])
async def list_inbound_lines(order_id: int, session: SessionDep) -> list[InboundOrderLineRead]:
    rows = list(await session.scalars(select(InboundOrderLine).where(InboundOrderLine.order_id == order_id)))
    return [InboundOrderLineRead.model_validate(r) for r in rows]


@router.post("/{order_id}/lines", response_model=InboundOrderLineRead, status_code=status.HTTP_201_CREATED, dependencies=[Depends(require_permission("create", "orders"))])
async def create_inbound_line(order_id: int, body: InboundOrderLineCreate, session: SessionDep, user_id: UserDep) -> InboundOrderLineRead:
    line = InboundOrderLine(order_id=order_id, created_by_id=user_id, updated_by_id=user_id, **body.model_dump(exclude={"order_id"}))
    session.add(line)
    await session.flush()
    return InboundOrderLineRead.model_validate(line)
