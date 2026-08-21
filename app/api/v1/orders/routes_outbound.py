"""API для исходящих заказов."""

from __future__ import annotations

from fastapi import APIRouter, Depends, status

from app.api.deps import SessionDep, UserDep, require_permission
from app.api.v1.orders.schemas_detailed import OutboundOrderDetailed
from app.api.v1.orders.schemas_enriched import OutboundOrderDetail, OutboundOrderLineList, OutboundOrderList
from app.api.v1.orders.schemas import (
    OutboundOrderCreate,
    OutboundOrderLineCreate,
    OutboundOrderLineRead,
    OutboundOrderRead,
    OutboundOrderUpdate,
)
from app.core.exceptions import NotFoundError
from app.core.statuses import OrderStatus
from app.orders.repository import OutboundOrderLineRepository, OutboundOrderRepository
from app.orders.models import OutboundOrder, OutboundOrderLine
from app.parties.models import Address, Client, Depositor
from app.api.v1.parties.schemas import AddressRead, ClientRead, DeliveryZoneRead, DepositorRead
from app.api.v1.warehouse.schemas import WarehouseRead

router = APIRouter(prefix="/outbound-orders", tags=["outbound-orders"])


@router.get(
    "/list",
    response_model=list[OutboundOrderList],
    dependencies=[Depends(require_permission("view", "orders"))],
)
async def list_outbound_orders_for_table(
    session: SessionDep,
) -> list[OutboundOrderList]:
    """Плоский список для таблицы."""
    from sqlalchemy import select as sa_select
    from sqlalchemy.orm import selectinload

    stmt = (
        sa_select(OutboundOrder)
        .options(selectinload(OutboundOrder.depositor).selectinload(Depositor.legal_entity))
        .options(selectinload(OutboundOrder.client).selectinload(Client.delivery_address).selectinload(Address.delivery_zone))
        .options(selectinload(OutboundOrder.warehouse))
    )
    rows = list(await session.scalars(stmt))

    result = []
    for r in rows:
        result.append(
            OutboundOrderList(
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
                customer_code=r.customer_code,
                customer_name=r.customer_name,
                document_number=r.document_number,
                delivery_address_name=r.delivery_address_name,
                order_date=r.order_date,
                shipping_date=r.shipping_date,
                status=r.status,
                status_label=(
                    OrderStatus(r.status).label
                    if r.status in OrderStatus._value2member_map_
                    else r.status
                ),
                is_edo=r.is_edo,
                warehouse_id=r.warehouse_id,
                declared_weight=r.declared_weight,
                needs_delivery=r.needs_delivery,
                notes=r.notes,
                depositor_name=(
                    r.depositor.legal_entity.name
                    if r.depositor and r.depositor.legal_entity
                    else None
                ),
                zone_name=r.client.delivery_address.delivery_zone.name if r.client and r.client.delivery_address and r.client.delivery_address.delivery_zone else None,
                warehouse_name=r.warehouse.name if r.warehouse else None,
                route_number=None,
                driver_name=None,
                driver_phone=None,
            )
        )
    return result


@router.get(
    "/{order_id}/detail",
    response_model=OutboundOrderDetail,
    dependencies=[Depends(require_permission("view", "orders"))],
)
async def get_outbound_order_detail(
    order_id: int, session: SessionDep
) -> OutboundOrderDetail:
    """Вложенная схема для детальной страницы."""
    from sqlalchemy import select as sa_select
    from sqlalchemy.orm import selectinload

    stmt = (
        sa_select(OutboundOrder)
        .where(OutboundOrder.id == order_id)
        .options(selectinload(OutboundOrder.depositor).selectinload(Depositor.legal_entity))
        .options(selectinload(OutboundOrder.client).selectinload(Client.delivery_address).selectinload(Address.delivery_zone))
        .options(selectinload(OutboundOrder.warehouse))
    )
    order = await session.scalar(stmt)
    if order is None:
        raise NotFoundError("Заказ не найден")

    return OutboundOrderDetail(
        id=order.id,
        is_active=order.is_active,
        is_deleted=order.is_deleted,
        created_at=order.created_at,
        updated_at=order.updated_at,
        created_by_id=order.created_by_id,
        updated_by_id=order.updated_by_id,
        deleted_at=order.deleted_at,
        deleted_by_id=order.deleted_by_id,
        number=order.number,
        customer_code=order.customer_code,
        customer_name=order.customer_name,
        document_number=order.document_number,
        delivery_address_name=order.delivery_address_name,
        order_date=order.order_date,
        shipping_date=order.shipping_date,
        status=order.status,
        is_edo=order.is_edo,
        warehouse_id=order.warehouse_id,
        declared_weight=order.declared_weight,
        needs_delivery=order.needs_delivery,
        delivery_only=order.delivery_only,
        places_count=order.places_count,
        delivery_contact=order.delivery_contact,
        notes=order.notes,
        depositor=DepositorRead.model_validate(order.depositor) if order.depositor else None,
        client=ClientRead.model_validate(order.client) if order.client else None,
        warehouse=WarehouseRead.model_validate(order.warehouse) if order.warehouse else None,
        delivery_order=None,
        route=None,
        driver=None,
        delivery_address=AddressRead.model_validate(order.client.delivery_address) if order.client and order.client.delivery_address else None,
        zone=DeliveryZoneRead.model_validate(order.client.delivery_address.delivery_zone) if order.client and order.client.delivery_address and order.client.delivery_address.delivery_zone else None,
        documents=await _get_order_documents(session, order),
        tasks=await _get_order_tasks(session, order),
        returns=await _get_order_returns(session, order),
    )


@router.get(
    "/detailed",
    response_model=list[OutboundOrderDetailed],
    dependencies=[Depends(require_permission("view", "orders"))],
)
async def list_outbound_orders_detailed(
    session: SessionDep,
) -> list[OutboundOrderDetailed]:
    repo = OutboundOrderRepository(session)
    rows = await repo.list_all_detailed()
    return [OutboundOrderDetailed.model_validate(r) for r in rows]


@router.get(
    "",
    response_model=list[OutboundOrderRead],
    dependencies=[Depends(require_permission("view", "orders"))],
)
async def list_outbound_orders(session: SessionDep,
) -> list[OutboundOrderRead]:
    repo = OutboundOrderRepository(session)
    rows = await repo.list_all()
    return [OutboundOrderRead.model_validate(r) for r in rows]


@router.post(
    "",
    response_model=OutboundOrderRead,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_permission("create", "orders"))],
)
async def create_outbound_order(
    body: OutboundOrderCreate, session: SessionDep, user_id: UserDep
) -> OutboundOrderRead:
    order = OutboundOrder(created_by_id=user_id, **body.model_dump())
    session.add(order)
    await session.flush()
    return OutboundOrderRead.model_validate(order)


@router.get(
    "/{order_id}",
    response_model=OutboundOrderRead,
    dependencies=[Depends(require_permission("view", "orders"))],
)
async def get_outbound_order(order_id: int, session: SessionDep) -> OutboundOrderRead:
    order = await OutboundOrderRepository(session).get_by_id(order_id)
    if order is None:
        raise NotFoundError("Заявка не найдена")
    return OutboundOrderRead.model_validate(order)


@router.patch(
    "/{order_id}",
    response_model=OutboundOrderRead,
    dependencies=[Depends(require_permission("update", "orders"))],
)
async def update_outbound_order(
    order_id: int, body: OutboundOrderUpdate, session: SessionDep, user_id: UserDep
) -> OutboundOrderRead:
    order = await OutboundOrderRepository(session).get_by_id(order_id)
    if order is None:
        raise NotFoundError("Заявка не найдена")
    for field, value in body.model_dump(exclude_unset=True).items():
        setattr(order, field, value)
    order.updated_by_id = user_id
    await session.flush()
    return OutboundOrderRead.model_validate(order)


@router.delete(
    "/{order_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(require_permission("delete", "orders"))],
)
async def delete_outbound_order(
    order_id: int, session: SessionDep, user_id: UserDep
) -> None:
    order = await OutboundOrderRepository(session).get_by_id(order_id)
    if order is None:
        raise NotFoundError("Заявка не найдена")
    order.soft_delete(user_id)
    await session.flush()


# ========== Строки ==========


@router.get(
    "/{order_id}/lines/enriched",
    response_model=list[OutboundOrderLineList],
    dependencies=[Depends(require_permission("view", "orders"))],
)
async def list_outbound_lines_enriched(
    order_id: int, session: SessionDep
) -> list[OutboundOrderLineList]:
    """Строки заказа с названиями товаров."""
    from sqlalchemy import select as sa_select
    from sqlalchemy.orm import selectinload
    from app.warehouse.models import Product, Location

    stmt = (
        sa_select(OutboundOrderLine)
        .where(OutboundOrderLine.order_id == order_id)
        .options(selectinload(OutboundOrderLine.product))
        .options(selectinload(OutboundOrderLine.location))
    )
    rows = list(await session.scalars(stmt))

    result = []
    for line in rows:
        result.append(OutboundOrderLineList(
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
            location_id=line.location_id,
            batch_number=line.batch_number,
            manufacture_date=line.manufacture_date,
            product_name=line.product.name if line.product else None,
            product_sku=line.product.sku if line.product else None,
            location_name=None,
        ))
    return result


@router.get(
    "/{order_id}/lines",
    response_model=list[OutboundOrderLineRead],
    dependencies=[Depends(require_permission("view", "orders"))],
)
async def list_outbound_lines(
    order_id: int, session: SessionDep
) -> list[OutboundOrderLineRead]:
    rows = await OutboundOrderLineRepository(session).list_by_order(order_id)
    return [OutboundOrderLineRead.model_validate(r) for r in rows]


@router.get(
    "/lines/{line_id}",
    response_model=OutboundOrderLineRead,
    dependencies=[Depends(require_permission("view", "orders"))],
)
async def get_outbound_line(line_id: int, session: SessionDep) -> OutboundOrderLineRead:
    line = await OutboundOrderLineRepository(session).get_by_id(line_id)
    if line is None:
        raise NotFoundError("Строка не найдена")
    return OutboundOrderLineRead.model_validate(line)


@router.patch(
    "/lines/{line_id}",
    response_model=OutboundOrderLineRead,
    dependencies=[Depends(require_permission("update", "orders"))],
)
async def update_outbound_line(
    line_id: int, body: OutboundOrderLineCreate, session: SessionDep, user_id: UserDep
) -> OutboundOrderLineRead:
    line = await OutboundOrderLineRepository(session).get_by_id(line_id)
    if line is None:
        raise NotFoundError("Строка не найдена")
    for field, value in body.model_dump(
        exclude_unset=True, exclude={"order_id"}
    ).items():
        setattr(line, field, value)
    line.updated_by_id = user_id
    await session.flush()
    return OutboundOrderLineRead.model_validate(line)


@router.delete(
    "/lines/{line_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(require_permission("delete", "orders"))],
)
async def delete_outbound_line(
    line_id: int, session: SessionDep, user_id: UserDep
) -> None:
    line = await OutboundOrderLineRepository(session).get_by_id(line_id)
    if line is None:
        raise NotFoundError("Строка не найдена")
    line.soft_delete(user_id)
    await session.flush()


@router.post(
    "/{order_id}/lines",
    response_model=OutboundOrderLineRead,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_permission("create", "orders"))],
)
async def create_outbound_line(
    order_id: int, body: OutboundOrderLineCreate, session: SessionDep, user_id: UserDep
) -> OutboundOrderLineRead:
    line = OutboundOrderLine(order_id=order_id, **body.model_dump(exclude={"order_id"}))
    session.add(line)
    await session.flush()
    return OutboundOrderLineRead.model_validate(line)


async def _get_order_documents(session, order):
    """Складские документы по номеру заказа."""
    from app.documents.models import Document
    from sqlalchemy import select as sa_select
    stmt = sa_select(Document).where(Document.document_number == order.number)
    rows = list(await session.scalars(stmt))
    return [{"id": d.id, "document_number": d.document_number, "document_type": d.document_type, "status": d.status} for d in rows]


async def _get_order_tasks(session, order):
    """Задания по документам заказа."""
    from app.warehouse.models import Task
    from sqlalchemy import select as sa_select
    docs = await _get_order_documents(session, order)
    doc_ids = [d["id"] for d in docs]
    if not doc_ids:
        return []
    stmt = sa_select(Task).where(Task.document_id.in_(doc_ids))
    rows = list(await session.scalars(stmt))
    return [{"id": t.id, "task_type": t.task_type, "status": t.status} for t in rows]


async def _get_order_returns(session, order):
    """Возвраты по заказу."""
    from app.orders.models import ReturnOrder
    from sqlalchemy import select as sa_select
    stmt = sa_select(ReturnOrder).where(ReturnOrder.outbound_order_id == order.id)
    rows = list(await session.scalars(stmt))
    return [{"id": r.id, "return_date": r.return_date, "status": r.status, "return_type": r.return_type} for r in rows]
