"""API для возвратов."""

from __future__ import annotations

from fastapi import APIRouter, Depends, status

from app.api.deps import ScopeDep, Services, UserDep, require_permission
from app.api.v1.orders.schemas import (
    ReturnOrderCreate,
    ReturnOrderLineCreate,
    ReturnOrderLineRead,
    ReturnOrderRead,
    ReturnOrderUpdate,
)
from app.core.exceptions import NotFoundError
from app.orders.repository import ReturnOrderLineRepository

router = APIRouter(prefix="/return-orders", tags=["return-orders"])


@router.get("", response_model=list[ReturnOrderRead], dependencies=[Depends(require_permission("view", "orders"))])
async def list_return_orders(services: Services, scope: ScopeDep) -> list[ReturnOrderRead]:
    rows = await services.return_order.list_all(scope)
    return [ReturnOrderRead.model_validate(r) for r in rows]


@router.post("", response_model=ReturnOrderRead, status_code=status.HTTP_201_CREATED, dependencies=[Depends(require_permission("create", "orders"))])
async def create_return_order(body: ReturnOrderCreate, services: Services, scope: ScopeDep) -> ReturnOrderRead:
    order = await services.return_order.create(scope=scope, **body.model_dump())
    return ReturnOrderRead.model_validate(order)


@router.get("/{order_id}", response_model=ReturnOrderRead, dependencies=[Depends(require_permission("view", "orders"))])
async def get_return_order(order_id: int, services: Services, scope: ScopeDep) -> ReturnOrderRead:
    order = await services.return_order.get_by_id(order_id, scope)
    if order is None:
        raise NotFoundError("Возврат не найден")
    return ReturnOrderRead.model_validate(order)


@router.patch("/{order_id}", response_model=ReturnOrderRead, dependencies=[Depends(require_permission("update", "orders"))])
async def update_return_order(order_id: int, body: ReturnOrderUpdate, services: Services, scope: ScopeDep) -> ReturnOrderRead:
    order = await services.return_order.update(order_id, scope, **body.model_dump(exclude_unset=True))
    if order is None:
        raise NotFoundError("Возврат не найден")
    return ReturnOrderRead.model_validate(order)


@router.delete("/{order_id}", status_code=status.HTTP_204_NO_CONTENT, dependencies=[Depends(require_permission("delete", "orders"))])
async def delete_return_order(order_id: int, services: Services, user_id: UserDep, scope: ScopeDep) -> None:
    ok = await services.return_order.soft_delete(order_id, user_id, scope)
    if not ok:
        raise NotFoundError("Возврат не найден")


@router.get("/{order_id}/lines", response_model=list[ReturnOrderLineRead], dependencies=[Depends(require_permission("view", "orders"))])
async def list_return_lines(order_id: int, services: Services, scope: ScopeDep) -> list[ReturnOrderLineRead]:
    order = await services.return_order.get_by_id(order_id, scope)
    if order is None:
        raise NotFoundError("Возврат не найден")
    rows = await services.return_order.list_lines(order_id)
    return [ReturnOrderLineRead.model_validate(r) for r in rows]


@router.post("/{order_id}/lines", response_model=ReturnOrderLineRead, status_code=status.HTTP_201_CREATED, dependencies=[Depends(require_permission("create", "orders"))])
async def create_return_line(order_id: int, body: ReturnOrderLineCreate, services: Services, scope: ScopeDep, user_id: UserDep) -> ReturnOrderLineRead:
    order = await services.return_order.get_by_id(order_id, scope)
    if order is None:
        raise NotFoundError("Возврат не найден")
    line = await services.return_order.add_line(
        user_id=user_id,
        return_order_id=order_id,
        **body.model_dump(exclude={"return_order_id"}),
    )
    return ReturnOrderLineRead.model_validate(line)


@router.delete("/lines/{line_id}", status_code=status.HTTP_204_NO_CONTENT, dependencies=[Depends(require_permission("delete", "orders"))])
async def delete_return_line(line_id: int, services: Services, user_id: UserDep) -> None:
    ok = await ReturnOrderLineRepository(services.session).soft_delete(line_id, user_id)
    if not ok:
        raise NotFoundError("Строка не найдена")
