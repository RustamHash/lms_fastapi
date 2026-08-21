"""API для отклонений и строк маршрутов."""

from __future__ import annotations

from fastapi import APIRouter, Depends, status
from sqlalchemy import select

from app.api.deps import SessionDep, UserDep, require_permission
from app.core.exceptions import NotFoundError
from app.delivery.models import DeliveryDeviation, RouteLine
from app.infrastructure.events import event_bus
from app.infrastructure.events.event_types import EventTypes

router = APIRouter(tags=["delivery-deviations-lines"])


# ========== Отклонения ==========

@router.get(
    "/deviations",
    response_model=list[dict],
    dependencies=[Depends(require_permission("view", "delivery"))],
)
async def list_deviations(
    session: SessionDep,
    delivery_order_id: int | None = None,
) -> list[dict]:
    stmt = select(DeliveryDeviation)
    if delivery_order_id:
        stmt = stmt.where(DeliveryDeviation.delivery_order_id == delivery_order_id)
    rows = list(await session.scalars(stmt))
    return [
        {
            "id": d.id,
            "delivery_order_id": d.delivery_order_id,
            "deviation_type": d.deviation_type,
            "quantity": d.quantity,
            "description": d.description,
            "is_active": d.is_active,
            "is_deleted": d.is_deleted,
            "created_at": d.created_at,
            "updated_at": d.updated_at,
            "created_by_id": d.created_by_id,
            "updated_by_id": d.updated_by_id,
            "deleted_at": d.deleted_at,
            "deleted_by_id": d.deleted_by_id,
        }
        for d in rows
    ]


@router.post(
    "/deviations",
    response_model=dict,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_permission("create", "delivery"))],
)
async def create_deviation(
    body: dict,
    session: SessionDep,
    user_id: UserDep,
) -> dict:
    deviation = DeliveryDeviation(
        delivery_order_id=body["delivery_order_id"],
        deviation_type=body["deviation_type"],
        quantity=body.get("quantity", 0),
        description=body.get("description", ""),
        created_by_id=user_id,
        updated_by_id=user_id,
    )
    session.add(deviation)
    await session.flush()
    return {"id": deviation.id}


@router.get(
    "/deviations/{deviation_id}",
    response_model=dict,
    dependencies=[Depends(require_permission("view", "delivery"))],
)
async def get_deviation(deviation_id: int, session: SessionDep) -> dict:
    d = await session.get(DeliveryDeviation, deviation_id)
    if d is None:
        raise NotFoundError("Отклонение не найдено")
    return {
        "id": d.id,
        "delivery_order_id": d.delivery_order_id,
        "deviation_type": d.deviation_type,
        "quantity": d.quantity,
        "description": d.description,
        "is_active": d.is_active,
        "is_deleted": d.is_deleted,
        "created_at": d.created_at,
        "updated_at": d.updated_at,
        "created_by_id": d.created_by_id,
        "updated_by_id": d.updated_by_id,
        "deleted_at": d.deleted_at,
        "deleted_by_id": d.deleted_by_id,
    }


@router.patch(
    "/deviations/{deviation_id}",
    response_model=dict,
    dependencies=[Depends(require_permission("update", "delivery"))],
)
async def update_deviation(
    deviation_id: int,
    body: dict,
    session: SessionDep,
    user_id: UserDep,
) -> dict:
    d = await session.get(DeliveryDeviation, deviation_id)
    if d is None:
        raise NotFoundError("Отклонение не найдено")
    for field in ["deviation_type", "quantity", "description"]:
        if field in body:
            setattr(d, field, body[field])
    d.updated_by_id = user_id
    await session.flush()
    return {"id": d.id}


@router.delete(
    "/deviations/{deviation_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(require_permission("delete", "delivery"))],
)
async def delete_deviation(
    deviation_id: int,
    session: SessionDep,
    user_id: UserDep,
) -> None:
    d = await session.get(DeliveryDeviation, deviation_id)
    if d is None:
        raise NotFoundError("Отклонение не найдено")
    d.soft_delete(user_id)
    await session.flush()


# ========== Строки маршрута ==========

@router.get(
    "/route-lines",
    response_model=list[dict],
    dependencies=[Depends(require_permission("view", "routes"))],
)
async def list_route_lines(
    session: SessionDep,
    route_id: int | None = None,
) -> list[dict]:
    stmt = select(RouteLine)
    if route_id:
        stmt = stmt.where(RouteLine.route_id == route_id)
    rows = list(await session.scalars(stmt))
    return [
        {
            "id": rl.id,
            "route_id": rl.route_id,
            "delivery_order_id": rl.delivery_order_id,
            "order": rl.order,
            "planned_time": rl.planned_time,
            "actual_time": rl.actual_time,
            "status": rl.status,
            "is_active": rl.is_active,
            "is_deleted": rl.is_deleted,
            "created_at": rl.created_at,
            "updated_at": rl.updated_at,
            "created_by_id": rl.created_by_id,
            "updated_by_id": rl.updated_by_id,
            "deleted_at": rl.deleted_at,
            "deleted_by_id": rl.deleted_by_id,
        }
        for rl in rows
    ]


@router.post(
    "/route-lines",
    response_model=dict,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_permission("create", "routes"))],
)
async def create_route_line(
    body: dict,
    session: SessionDep,
    user_id: UserDep,
) -> dict:
    rl = RouteLine(
        route_id=body["route_id"],
        delivery_order_id=body["delivery_order_id"],
        order=body.get("order", 0),
        planned_time=body.get("planned_time"),
        actual_time=body.get("actual_time"),
        status=body.get("status", "pending"),
        created_by_id=user_id,
        updated_by_id=user_id,
    )
    session.add(rl)
    await session.flush()

    # Отправить событие о назначении маршрута
    await event_bus.emit(EventTypes.ROUTE_ASSIGNED, {
        "_event_type": EventTypes.ROUTE_ASSIGNED,
        "route_id": rl.route_id,
        "route_number": rl.route_id,
        "delivery_order_id": rl.delivery_order_id,
    })

    return {"id": rl.id}


@router.get(
    "/route-lines/{line_id}",
    response_model=dict,
    dependencies=[Depends(require_permission("view", "routes"))],
)
async def get_route_line(line_id: int, session: SessionDep) -> dict:
    rl = await session.get(RouteLine, line_id)
    if rl is None:
        raise NotFoundError("Строка маршрута не найдена")
    return {
        "id": rl.id,
        "route_id": rl.route_id,
        "delivery_order_id": rl.delivery_order_id,
        "order": rl.order,
        "planned_time": rl.planned_time,
        "actual_time": rl.actual_time,
        "status": rl.status,
        "is_active": rl.is_active,
        "is_deleted": rl.is_deleted,
        "created_at": rl.created_at,
        "updated_at": rl.updated_at,
        "created_by_id": rl.created_by_id,
        "updated_by_id": rl.updated_by_id,
        "deleted_at": rl.deleted_at,
        "deleted_by_id": rl.deleted_by_id,
    }


@router.patch(
    "/route-lines/{line_id}",
    response_model=dict,
    dependencies=[Depends(require_permission("update", "routes"))],
)
async def update_route_line(
    line_id: int,
    body: dict,
    session: SessionDep,
    user_id: UserDep,
) -> dict:
    rl = await session.get(RouteLine, line_id)
    if rl is None:
        raise NotFoundError("Строка маршрута не найдена")
    for field in ["order", "planned_time", "actual_time", "status"]:
        if field in body:
            setattr(rl, field, body[field])
    rl.updated_by_id = user_id
    await session.flush()
    return {"id": rl.id}


@router.delete(
    "/route-lines/{line_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(require_permission("delete", "routes"))],
)
async def delete_route_line(
    line_id: int,
    session: SessionDep,
    user_id: UserDep,
) -> None:
    rl = await session.get(RouteLine, line_id)
    if rl is None:
        raise NotFoundError("Строка маршрута не найдена")
    rl.soft_delete(user_id)
    await session.flush()
