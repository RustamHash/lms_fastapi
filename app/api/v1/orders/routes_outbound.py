"""API для исходящих заказов."""

from __future__ import annotations

from fastapi import APIRouter, Depends, status
from sqlalchemy import select

from app.api.deps import SessionDep, UserDep, require_permission
from app.api.v1.orders.schemas import (
    OutboundOrderCreate,
    OutboundOrderLineCreate,
    OutboundOrderLineRead,
    OutboundOrderRead,
    OutboundOrderUpdate,
)
from app.core.exceptions import NotFoundError
from app.orders.models import OutboundOrder, OutboundOrderLine

router = APIRouter(prefix="/outbound-orders", tags=["outbound-orders"])


@router.get("", response_model=list[OutboundOrderRead], dependencies=[Depends(require_permission("view", "orders"))])
async def list_outbound_orders(session: SessionDep) -> list[OutboundOrderRead]:
    rows = list(await session.scalars(select(OutboundOrder)))
    return [OutboundOrderRead.model_validate(r) for r in rows]


@router.post("", response_model=OutboundOrderRead, status_code=status.HTTP_201_CREATED, dependencies=[Depends(require_permission("create", "orders"))])
async def create_outbound_order(body: OutboundOrderCreate, session: SessionDep, user_id: UserDep) -> OutboundOrderRead:
    order = OutboundOrder(created_by_id=user_id, updated_by_id=user_id, **body.model_dump())
    session.add(order)
    await session.flush()
    return OutboundOrderRead.model_validate(order)


@router.get("/{order_id}", response_model=OutboundOrderRead, dependencies=[Depends(require_permission("view", "orders"))])
async def get_outbound_order(order_id: int, session: SessionDep) -> OutboundOrderRead:
    order = await session.get(OutboundOrder, order_id)
    if order is None:
        raise NotFoundError("Заявка не найдена")
    return OutboundOrderRead.model_validate(order)


@router.patch("/{order_id}", response_model=OutboundOrderRead, dependencies=[Depends(require_permission("update", "orders"))])
async def update_outbound_order(order_id: int, body: OutboundOrderUpdate, session: SessionDep, user_id: UserDep) -> OutboundOrderRead:
    order = await session.get(OutboundOrder, order_id)
    if order is None:
        raise NotFoundError("Заявка не найдена")
    for field, value in body.model_dump(exclude_unset=True).items():
        setattr(order, field, value)
    order.updated_by_id = user_id
    await session.flush()
    return OutboundOrderRead.model_validate(order)


@router.delete("/{order_id}", status_code=status.HTTP_204_NO_CONTENT, dependencies=[Depends(require_permission("delete", "orders"))])
async def delete_outbound_order(order_id: int, session: SessionDep, user_id: UserDep) -> None:
    order = await session.get(OutboundOrder, order_id)
    if order is None:
        raise NotFoundError("Заявка не найдена")
    order.soft_delete(user_id)
    await session.flush()


# ========== Строки ==========

@router.get("/{order_id}/lines", response_model=list[OutboundOrderLineRead], dependencies=[Depends(require_permission("view", "orders"))])
async def list_outbound_lines(order_id: int, session: SessionDep) -> list[OutboundOrderLineRead]:
    rows = list(await session.scalars(select(OutboundOrderLine).where(OutboundOrderLine.order_id == order_id)))
    return [OutboundOrderLineRead.model_validate(r) for r in rows]


@router.get("/lines/{line_id}", response_model=OutboundOrderLineRead, dependencies=[Depends(require_permission("view", "orders"))])
async def get_outbound_line(line_id: int, session: SessionDep) -> OutboundOrderLineRead:
    line = await session.get(OutboundOrderLine, line_id)
    if line is None:
        raise NotFoundError("Строка не найдена")
    return OutboundOrderLineRead.model_validate(line)


@router.patch("/lines/{line_id}", response_model=OutboundOrderLineRead, dependencies=[Depends(require_permission("update", "orders"))])
async def update_outbound_line(line_id: int, body: OutboundOrderLineCreate, session: SessionDep, user_id: UserDep) -> OutboundOrderLineRead:
    line = await session.get(OutboundOrderLine, line_id)
    if line is None:
        raise NotFoundError("Строка не найдена")
    for field, value in body.model_dump(exclude_unset=True, exclude={"order_id"}).items():
        setattr(line, field, value)
    line.updated_by_id = user_id
    await session.flush()
    return OutboundOrderLineRead.model_validate(line)


@router.delete("/lines/{line_id}", status_code=status.HTTP_204_NO_CONTENT, dependencies=[Depends(require_permission("delete", "orders"))])
async def delete_outbound_line(line_id: int, session: SessionDep, user_id: UserDep) -> None:
    line = await session.get(OutboundOrderLine, line_id)
    if line is None:
        raise NotFoundError("Строка не найдена")
    line.soft_delete(user_id)
    await session.flush()


@router.post("/{order_id}/lines", response_model=OutboundOrderLineRead, status_code=status.HTTP_201_CREATED, dependencies=[Depends(require_permission("create", "orders"))])
async def create_outbound_line(order_id: int, body: OutboundOrderLineCreate, session: SessionDep, user_id: UserDep) -> OutboundOrderLineRead:
    line = OutboundOrderLine(order_id=order_id, created_by_id=user_id, updated_by_id=user_id, **body.model_dump(exclude={"order_id"}))
    session.add(line)
    await session.flush()
    return OutboundOrderLineRead.model_validate(line)
