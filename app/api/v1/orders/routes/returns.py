"""API для возвратов."""

from __future__ import annotations

from fastapi import APIRouter, Depends, status

from app.api.deps import Services, UserDep, require_permission
from app.api.v1.orders.schemas import (
    ReturnOrderCreate,
    ReturnOrderLineCreate,
    ReturnOrderLineRead,
    ReturnOrderRead,
    ReturnOrderUpdate,
)
from app.core.exceptions import NotFoundError
from app.orders.repository import ReturnOrderLineRepository, ReturnOrderRepository

router = APIRouter(prefix="/return-orders", tags=["return-orders"])


@router.get("", response_model=list[ReturnOrderRead], dependencies=[Depends(require_permission("view", "orders"))])
async def list_return_orders(services: Services) -> list[ReturnOrderRead]:
    rows = await ReturnOrderRepository(services.session).list_all()
    return [ReturnOrderRead.model_validate(r) for r in rows]


@router.post("", response_model=ReturnOrderRead, status_code=status.HTTP_201_CREATED, dependencies=[Depends(require_permission("create", "orders"))])
async def create_return_order(body: ReturnOrderCreate, services: Services, user_id: UserDep) -> ReturnOrderRead:
    order = await ReturnOrderRepository(services.session).create(**body.model_dump())
    return ReturnOrderRead.model_validate(order)


@router.get("/{order_id}", response_model=ReturnOrderRead, dependencies=[Depends(require_permission("view", "orders"))])
async def get_return_order(order_id: int, services: Services) -> ReturnOrderRead:
    order = await ReturnOrderRepository(services.session).get_by_id(order_id)
    if order is None:
        raise NotFoundError("Возврат не найден")
    return ReturnOrderRead.model_validate(order)


@router.patch("/{order_id}", response_model=ReturnOrderRead, dependencies=[Depends(require_permission("update", "orders"))])
async def update_return_order(order_id: int, body: ReturnOrderUpdate, services: Services, user_id: UserDep) -> ReturnOrderRead:
    order = await ReturnOrderRepository(services.session).update(order_id, **body.model_dump(exclude_unset=True))
    if order is None:
        raise NotFoundError("Возврат не найден")
    return ReturnOrderRead.model_validate(order)


@router.delete("/{order_id}", status_code=status.HTTP_204_NO_CONTENT, dependencies=[Depends(require_permission("delete", "orders"))])
async def delete_return_order(order_id: int, services: Services, user_id: UserDep) -> None:
    ok = await ReturnOrderRepository(services.session).soft_delete(order_id, user_id)
    if not ok:
        raise NotFoundError("Возврат не найден")


@router.get("/{order_id}/lines", response_model=list[ReturnOrderLineRead], dependencies=[Depends(require_permission("view", "orders"))])
async def list_return_lines(order_id: int, services: Services) -> list[ReturnOrderLineRead]:
    rows = await ReturnOrderLineRepository(services.session).list_by_order(order_id)
    return [ReturnOrderLineRead.model_validate(r) for r in rows]


@router.post("/{order_id}/lines", response_model=ReturnOrderLineRead, status_code=status.HTTP_201_CREATED, dependencies=[Depends(require_permission("create", "orders"))])
async def create_return_line(order_id: int, body: ReturnOrderLineCreate, services: Services, user_id: UserDep) -> ReturnOrderLineRead:
    line = await ReturnOrderLineRepository(services.session).create(return_order_id=order_id, **body.model_dump(exclude={"return_order_id"}))
    return ReturnOrderLineRead.model_validate(line)


@router.delete("/lines/{line_id}", status_code=status.HTTP_204_NO_CONTENT, dependencies=[Depends(require_permission("delete", "orders"))])
async def delete_return_line(line_id: int, services: Services, user_id: UserDep) -> None:
    ok = await ReturnOrderLineRepository(services.session).soft_delete(line_id, user_id)
    if not ok:
        raise NotFoundError("Строка не найдена")
