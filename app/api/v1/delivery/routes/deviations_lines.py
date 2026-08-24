"""API для отклонений и строк маршрутов."""

from __future__ import annotations

from fastapi import APIRouter, Depends, status
from pydantic import BaseModel

from app.api.deps import Services, UserDep, require_permission
from app.core.exceptions import NotFoundError
from app.delivery.repository import DeviationRepository, RouteLineRepository

router = APIRouter(tags=["delivery-deviations-lines"])


class DeviationCreate(BaseModel):
    delivery_order_id: int
    deviation_type: str
    quantity: int = 0
    description: str = ""


class RouteLineCreate(BaseModel):
    route_id: int
    delivery_order_id: int
    order: int = 0
    planned_time: str | None = None
    actual_time: str | None = None
    status: str = "pending"


@router.get("/deviations", response_model=list[dict], dependencies=[Depends(require_permission("view", "delivery"))])
async def list_deviations(services: Services, delivery_order_id: int | None = None) -> list[dict]:
    repo = DeviationRepository(services.session)
    if delivery_order_id:
        rows = await repo.list_by_order(delivery_order_id)
    else:
        rows = await repo.list_all()
    return [{"id": d.id, "delivery_order_id": d.delivery_order_id, "deviation_type": d.deviation_type, "quantity": d.quantity, "description": d.description} for d in rows]


@router.post("/deviations", response_model=dict, status_code=status.HTTP_201_CREATED, dependencies=[Depends(require_permission("create", "delivery"))])
async def create_deviation(body: DeviationCreate, services: Services, user_id: UserDep) -> dict:
    deviation = await DeviationRepository(services.session).create(**body.model_dump())
    return {"id": deviation.id}


@router.delete("/deviations/{deviation_id}", status_code=status.HTTP_204_NO_CONTENT, dependencies=[Depends(require_permission("delete", "delivery"))])
async def delete_deviation(deviation_id: int, services: Services, user_id: UserDep) -> None:
    ok = await DeviationRepository(services.session).soft_delete(deviation_id, user_id)
    if not ok:
        raise NotFoundError("Отклонение не найдено")


@router.get("/route-lines", response_model=list[dict], dependencies=[Depends(require_permission("view", "routes"))])
async def list_route_lines(services: Services, route_id: int | None = None) -> list[dict]:
    repo = RouteLineRepository(services.session)
    if route_id:
        rows = await repo.list_by_route(route_id)
    else:
        rows = await repo.list_all()
    return [{"id": rl.id, "route_id": rl.route_id, "delivery_order_id": rl.delivery_order_id, "order": rl.order, "status": rl.status} for rl in rows]


@router.post("/route-lines", response_model=dict, status_code=status.HTTP_201_CREATED, dependencies=[Depends(require_permission("create", "routes"))])
async def create_route_line(body: RouteLineCreate, services: Services, user_id: UserDep) -> dict:
    line = await RouteLineRepository(services.session).create(**body.model_dump())
    return {"id": line.id}


@router.delete("/route-lines/{line_id}", status_code=status.HTTP_204_NO_CONTENT, dependencies=[Depends(require_permission("delete", "routes"))])
async def delete_route_line(line_id: int, services: Services, user_id: UserDep) -> None:
    ok = await RouteLineRepository(services.session).soft_delete(line_id, user_id)
    if not ok:
        raise NotFoundError("Строка маршрута не найдена")
