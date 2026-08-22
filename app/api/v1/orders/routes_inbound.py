"""API для входящих заказов."""

from __future__ import annotations

from fastapi import HTTPException, APIRouter, Depends, status
from sqlalchemy import select

from app.api.deps import SessionDep, UserDep, require_permission
from app.api.v1.orders.schemas_detailed import InboundOrderDetailed
from app.api.v1.orders.schemas_enriched import InboundOrderDetail, InboundOrderLineList, InboundOrderList
from app.api.v1.orders.schemas import (
    InboundOrderCreate,
    InboundOrderLineCreate,
    InboundOrderLineRead,
    InboundOrderRead,
    InboundOrderUpdate,
)
from app.core.exceptions import NotFoundError
from app.orders.models import InboundOrder, InboundOrderLine
from app.parties.models import Depositor
from app.core.statuses import OrderStatus
from app.orders.repository import InboundOrderLineRepository, InboundOrderRepository

router = APIRouter(prefix="/inbound-orders", tags=["inbound-orders"])


@router.get("/list", response_model=list[InboundOrderList], dependencies=[Depends(require_permission("view", "orders"))])
async def list_inbound_orders_for_table(session: SessionDep,
) -> list[InboundOrderList]:
    """Плоский список для таблицы."""
    from sqlalchemy import select as sa_select
    from sqlalchemy.orm import selectinload

    stmt = (
        sa_select(InboundOrder)
        .options(selectinload(InboundOrder.depositor).selectinload(Depositor.legal_entity))
        .options(selectinload(InboundOrder.supplier))
        .options(selectinload(InboundOrder.warehouse))
    )
    rows = list(await session.scalars(stmt))

    result = []
    for r in rows:
        result.append(InboundOrderList(
            id=r.id,
            is_active=r.is_active,
            is_deleted=r.is_deleted,
            created_at=r.created_at,
            updated_at=r.updated_at,
            created_by_id=r.created_by_id,
            updated_by_id=r.updated_by_id,
            deleted_at=r.deleted_at,
            deleted_by_id=r.deleted_by_id,
            number=r.number,
            supplier_code=r.supplier_code,
            order_date=r.order_date,
            planned_date=r.planned_date,
            status=r.status,
            status_label=OrderStatus(r.status).label if r.status in OrderStatus._value2member_map_ else r.status,
            has_shortage=r.has_shortage,
            warehouse_id=r.warehouse_id,
            notes=r.notes,
            depositor_name=r.depositor.legal_entity.name if r.depositor and r.depositor.legal_entity else None,
            supplier_name=r.supplier.name if r.supplier else None,
            warehouse_name=r.warehouse.name if r.warehouse else None,
        ))
    return result


@router.get("/{order_id}/detail", response_model=InboundOrderDetail, dependencies=[Depends(require_permission("view", "orders"))])
async def get_inbound_order_detail(order_id: int, session: SessionDep) -> InboundOrderDetail:
    """Вложенная схема для детальной страницы."""
    order = await InboundOrderRepository(session).get_by_id(order_id)
    if order is None:
        raise NotFoundError("Заказ не найден")
    return InboundOrderDetail.model_validate(order)


@router.get("/detailed", response_model=list[InboundOrderDetailed], dependencies=[Depends(require_permission("view", "orders"))])
async def list_inbound_orders_detailed(session: SessionDep,
) -> list[InboundOrderDetailed]:
    repo = InboundOrderRepository(session)
    rows = await repo.list_all_detailed()
    return [InboundOrderDetailed.model_validate(r) for r in rows]


@router.get("", response_model=list[InboundOrderRead], dependencies=[Depends(require_permission("view", "orders"))])
async def list_inbound_orders(session: SessionDep,
) -> list[InboundOrderRead]:
    repo = InboundOrderRepository(session)
    rows = await repo.list_all()
    return [InboundOrderRead.model_validate(r) for r in rows]


@router.post("", response_model=InboundOrderRead, status_code=status.HTTP_201_CREATED, dependencies=[Depends(require_permission("create", "orders"))])
async def create_inbound_order(body: InboundOrderCreate, session: SessionDep, user_id: UserDep) -> InboundOrderRead:
    order = InboundOrder(created_by_id=user_id, **body.model_dump())
    session.add(order)
    try:
        await session.flush()
    except Exception as e:
        await session.rollback()
        raise HTTPException(status_code=500, detail=f"Ошибка базы данных: {e}")
    return InboundOrderRead.model_validate(order)


@router.get("/{order_id}", response_model=InboundOrderRead, dependencies=[Depends(require_permission("view", "orders"))])
async def get_inbound_order(order_id: int, session: SessionDep) -> InboundOrderRead:
    order = await InboundOrderRepository(session).get_by_id(order_id)
    if order is None:
        raise NotFoundError("Заявка не найдена")
    return InboundOrderRead.model_validate(order)


@router.patch("/{order_id}", response_model=InboundOrderRead, dependencies=[Depends(require_permission("update", "orders"))])
async def update_inbound_order(order_id: int, body: InboundOrderUpdate, session: SessionDep, user_id: UserDep) -> InboundOrderRead:
    order = await InboundOrderRepository(session).get_by_id(order_id)
    if order is None:
        raise NotFoundError("Заявка не найдена")
    for field, value in body.model_dump(exclude_unset=True).items():
        setattr(order, field, value)
    order.updated_by_id = user_id
    try:
        await session.flush()
    except Exception as e:
        await session.rollback()
        raise HTTPException(status_code=500, detail=f"Ошибка базы данных: {e}")
    return InboundOrderRead.model_validate(order)


@router.delete("/{order_id}", status_code=status.HTTP_204_NO_CONTENT, dependencies=[Depends(require_permission("delete", "orders"))])
async def delete_inbound_order(order_id: int, session: SessionDep, user_id: UserDep) -> None:
    order = await InboundOrderRepository(session).get_by_id(order_id)
    if order is None:
        raise NotFoundError("Заявка не найдена")
    order.soft_delete(user_id)
    try:
        await session.flush()
    except Exception as e:
        await session.rollback()
        raise HTTPException(status_code=500, detail=f"Ошибка базы данных: {e}")


# ========== Строки ==========

@router.get(
    "/{order_id}/lines/enriched",
    response_model=list[InboundOrderLineList],
    dependencies=[Depends(require_permission("view", "orders"))],
)
async def list_inbound_lines_enriched(
    order_id: int, session: SessionDep
) -> list[InboundOrderLineList]:
    """Строки приходного заказа с названиями товаров."""
    from sqlalchemy import select as sa_select
    from sqlalchemy.orm import selectinload

    stmt = (
        sa_select(InboundOrderLine)
        .where(InboundOrderLine.order_id == order_id)
        .options(selectinload(InboundOrderLine.product))
    )
    rows = list(await session.scalars(stmt))

    result = []
    for line in rows:
        result.append(InboundOrderLineList(
            id=line.id,
            is_active=line.is_active,
            is_deleted=line.is_deleted,
            created_at=line.created_at,
            updated_at=line.updated_at,
            created_by_id=line.created_by_id,
            updated_by_id=line.updated_by_id,
            deleted_at=line.deleted_at,
            deleted_by_id=line.deleted_by_id,
            order_id=line.order_id,
            product_id=line.product_id,
            quantity=line.quantity,
            batch_number=line.batch_number,
            manufacture_date=line.manufacture_date,
            product_name=line.product.name if line.product else None,
            product_sku=line.product.sku if line.product else None,
        ))
    return result


@router.get("/{order_id}/lines", response_model=list[InboundOrderLineRead], dependencies=[Depends(require_permission("view", "orders"))])
async def list_inbound_lines(order_id: int, session: SessionDep) -> list[InboundOrderLineRead]:
    rows = await InboundOrderLineRepository(session).list_by_order(order_id)
    return [InboundOrderLineRead.model_validate(r) for r in rows]


@router.get("/lines/{line_id}", response_model=InboundOrderLineRead, dependencies=[Depends(require_permission("view", "orders"))])
async def get_inbound_line(line_id: int, session: SessionDep) -> InboundOrderLineRead:
    line = await InboundOrderLineRepository(session).get_by_id(line_id)
    if line is None:
        raise NotFoundError("Строка не найдена")
    return InboundOrderLineRead.model_validate(line)


@router.patch("/lines/{line_id}", response_model=InboundOrderLineRead, dependencies=[Depends(require_permission("update", "orders"))])
async def update_inbound_line(line_id: int, body: InboundOrderLineCreate, session: SessionDep, user_id: UserDep) -> InboundOrderLineRead:
    line = await InboundOrderLineRepository(session).get_by_id(line_id)
    if line is None:
        raise NotFoundError("Строка не найдена")
    for field, value in body.model_dump(exclude_unset=True, exclude={"order_id"}).items():
        setattr(line, field, value)
    line.updated_by_id = user_id
    try:
        await session.flush()
    except Exception as e:
        await session.rollback()
        raise HTTPException(status_code=500, detail=f"Ошибка базы данных: {e}")
    return InboundOrderLineRead.model_validate(line)


@router.delete("/lines/{line_id}", status_code=status.HTTP_204_NO_CONTENT, dependencies=[Depends(require_permission("delete", "orders"))])
async def delete_inbound_line(line_id: int, session: SessionDep, user_id: UserDep) -> None:
    line = await InboundOrderLineRepository(session).get_by_id(line_id)
    if line is None:
        raise NotFoundError("Строка не найдена")
    line.soft_delete(user_id)
    try:
        await session.flush()
    except Exception as e:
        await session.rollback()
        raise HTTPException(status_code=500, detail=f"Ошибка базы данных: {e}")


@router.post("/{order_id}/lines", response_model=InboundOrderLineRead, status_code=status.HTTP_201_CREATED, dependencies=[Depends(require_permission("create", "orders"))])
async def create_inbound_line(order_id: int, body: InboundOrderLineCreate, session: SessionDep, user_id: UserDep) -> InboundOrderLineRead:
    line = InboundOrderLine(order_id=order_id, **body.model_dump(exclude={"order_id"}))
    session.add(line)
    try:
        await session.flush()
    except Exception as e:
        await session.rollback()
        raise HTTPException(status_code=500, detail=f"Ошибка базы данных: {e}")
    return InboundOrderLineRead.model_validate(line)
