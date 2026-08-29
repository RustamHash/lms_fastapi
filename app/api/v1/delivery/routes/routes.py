"""API для маршрутов."""

from __future__ import annotations

from fastapi import APIRouter, Depends, status

from app.api.deps import Services, UserDep, require_permission
from app.api.v1.delivery.schemas import (
    RouteAssignOrder,
    RouteCreate,
    RouteLineRead,
    RouteRead,
)
from app.core.exceptions import NotFoundError
from app.delivery.repository import RouteRepository

router = APIRouter(prefix="/delivery/routes", tags=["delivery-routes"])


@router.get("", response_model=list[RouteRead], dependencies=[Depends(require_permission("view", "routes"))])
async def list_routes(services: Services) -> list[RouteRead]:
    rows = await RouteRepository(services.session).list_all()
    return [RouteRead.model_validate(r) for r in rows]


@router.post("", response_model=RouteRead, status_code=status.HTTP_201_CREATED, dependencies=[Depends(require_permission("create", "routes"))])
async def create_route(body: RouteCreate, services: Services, user_id: UserDep) -> RouteRead:
    route = await RouteRepository(services.session).create(**body.model_dump())
    return RouteRead.model_validate(route)


@router.get("/{route_id}", response_model=RouteRead, dependencies=[Depends(require_permission("view", "routes"))])
async def get_route(route_id: int, services: Services) -> RouteRead:
    route = await RouteRepository(services.session).get_by_id(route_id)
    if route is None:
        raise NotFoundError("Маршрут не найден")
    return RouteRead.model_validate(route)


@router.post(
    "/{route_id}/assign",
    response_model=RouteLineRead,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_permission("update", "routes"))],
)
async def assign_order_to_route(
    route_id: int,
    body: RouteAssignOrder,
    services: Services,
    user_id: UserDep,
) -> RouteLineRead:
    line = await services.route.assign_order(
        route_id, body.delivery_order_id, user_id=user_id
    )
    return RouteLineRead.model_validate(line)


@router.patch("/{route_id}", response_model=RouteRead, dependencies=[Depends(require_permission("update", "routes"))])
async def update_route(route_id: int, body: RouteCreate, services: Services, user_id: UserDep) -> RouteRead:
    route = await RouteRepository(services.session).update(route_id, **body.model_dump(exclude_unset=True))
    if route is None:
        raise NotFoundError("Маршрут не найден")
    return RouteRead.model_validate(route)


@router.delete("/{route_id}", status_code=status.HTTP_204_NO_CONTENT, dependencies=[Depends(require_permission("delete", "routes"))])
async def delete_route(route_id: int, services: Services, user_id: UserDep) -> None:
    ok = await RouteRepository(services.session).soft_delete(route_id, user_id)
    if not ok:
        raise NotFoundError("Маршрут не найден")
