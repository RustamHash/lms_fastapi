"""API для заказов на доставку."""

from __future__ import annotations

from fastapi import APIRouter, Depends, status

from app.api.deps import ScopeDep, Services, UserDep, require_permission
from app.api.v1.delivery.schemas import DeliveryOrderCreate, DeliveryOrderRead
from app.core.exceptions import NotFoundError
from app.delivery.repository import DeliveryOrderRepository

router = APIRouter(prefix="/delivery/orders", tags=["delivery-orders"])


@router.get("", response_model=list[DeliveryOrderRead], dependencies=[Depends(require_permission("view", "delivery"))])
async def list_orders(services: Services, scope: ScopeDep) -> list[DeliveryOrderRead]:
    rows = await DeliveryOrderRepository(services.session).list_all(scope)
    return [DeliveryOrderRead.model_validate(r) for r in rows]


@router.post("", response_model=DeliveryOrderRead, status_code=status.HTTP_201_CREATED, dependencies=[Depends(require_permission("create", "delivery"))])
async def create_order(body: DeliveryOrderCreate, services: Services, user_id: UserDep) -> DeliveryOrderRead:
    order = await DeliveryOrderRepository(services.session).create(**body.model_dump())
    return DeliveryOrderRead.model_validate(order)


@router.get("/{order_id}", response_model=DeliveryOrderRead, dependencies=[Depends(require_permission("view", "delivery"))])
async def get_order(order_id: int, services: Services, scope: ScopeDep) -> DeliveryOrderRead:
    order = await DeliveryOrderRepository(services.session).get_by_id(order_id, scope)
    if order is None:
        raise NotFoundError("Заказ не найден")
    return DeliveryOrderRead.model_validate(order)


@router.patch("/{order_id}", response_model=DeliveryOrderRead, dependencies=[Depends(require_permission("update", "delivery"))])
async def update_order(order_id: int, body: DeliveryOrderCreate, services: Services, user_id: UserDep, scope: ScopeDep) -> DeliveryOrderRead:
    existing = await DeliveryOrderRepository(services.session).get_by_id(order_id, scope)
    if existing is None:
        raise NotFoundError("Заказ не найден")
    order = await DeliveryOrderRepository(services.session).update(order_id, **body.model_dump(exclude_unset=True))
    if order is None:
        raise NotFoundError("Заказ не найден")
    return DeliveryOrderRead.model_validate(order)


@router.delete("/{order_id}", status_code=status.HTTP_204_NO_CONTENT, dependencies=[Depends(require_permission("delete", "delivery"))])
async def delete_order(order_id: int, services: Services, user_id: UserDep, scope: ScopeDep) -> None:
    existing = await DeliveryOrderRepository(services.session).get_by_id(order_id, scope)
    if existing is None:
        raise NotFoundError("Заказ не найден")
    ok = await DeliveryOrderRepository(services.session).soft_delete(order_id, user_id)
    if not ok:
        raise NotFoundError("Заказ не найден")
