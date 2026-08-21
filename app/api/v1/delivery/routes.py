"""API для модуля delivery."""

from __future__ import annotations

from fastapi import APIRouter, Depends, status
from sqlalchemy import select

from app.api.deps import SessionDep, UserDep, require_permission
from app.api.v1.delivery import schemas
from app.core.exceptions import NotFoundError
from app.delivery.models import DeliveryOrder, Driver, Route, Vehicle
from app.infrastructure.events import event_bus
from app.infrastructure.events.event_types import EventTypes
from app.delivery.services import DeliveryOrderService

router = APIRouter(prefix="/delivery", tags=["delivery"])


# ========== Заказы на доставку ==========


@router.get("/orders", response_model=list[schemas.DeliveryOrderRead], dependencies=[Depends(require_permission("view", "delivery"))])
async def list_orders(
    session: SessionDep,
) -> list[schemas.DeliveryOrderRead]:
    service = DeliveryOrderService(session)
    rows = await service.list_all()
    return [schemas.DeliveryOrderRead.model_validate(r) for r in rows]


@router.post(
    "/orders",
    response_model=schemas.DeliveryOrderRead,
    status_code=status.HTTP_201_CREATED,
)
async def create_order(
    body: schemas.DeliveryOrderCreate,
    session: SessionDep,
    user_id: UserDep,
) -> schemas.DeliveryOrderRead:
    service = DeliveryOrderService(session)
    order = await service.create(user_id=user_id, **body.model_dump())
    return schemas.DeliveryOrderRead.model_validate(order)


@router.get("/orders/{order_id}", response_model=schemas.DeliveryOrderRead, dependencies=[Depends(require_permission("view", "delivery"))])
async def get_order(order_id: int, session: SessionDep) -> schemas.DeliveryOrderRead:
    service = DeliveryOrderService(session)
    order = await service.get_by_id(order_id)
    if order is None:
        raise NotFoundError("Заказ не найден")
    return schemas.DeliveryOrderRead.model_validate(order)


@router.delete(
    "/orders/{order_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(require_permission("delete", "delivery"))],
)
async def delete_order(order_id: int, session: SessionDep, user_id: UserDep) -> None:
    order = await session.get(DeliveryOrder, order_id)
    if order is None:
        raise NotFoundError("Заказ не найден")
    order.soft_delete(user_id)
    await session.flush()


@router.patch("/orders/{order_id}/status", response_model=schemas.DeliveryOrderRead, dependencies=[Depends(require_permission("update", "delivery"))])
async def update_order_status(
    order_id: int,
    body: schemas.DeliveryOrderStatusUpdate,
    session: SessionDep,
    user_id: UserDep,
) -> schemas.DeliveryOrderRead:
    service = DeliveryOrderService(session)
    order = await service.set_status(
        user_id=user_id,
        order_id=order_id,
        status=body.status,
    )
    if order is None:
        raise NotFoundError("Заказ не найден")
    return schemas.DeliveryOrderRead.model_validate(order)


# ========== Водители ==========


@router.get("/drivers", response_model=list[schemas.DriverRead], dependencies=[Depends(require_permission("view", "drivers"))])
async def list_drivers(session: SessionDep) -> list[schemas.DriverRead]:
    rows = list(
        await session.scalars(select(Driver).where())
    )
    return [schemas.DriverRead.model_validate(r) for r in rows]


@router.post(
    "/drivers", response_model=schemas.DriverRead, status_code=status.HTTP_201_CREATED
)
async def create_driver(
    body: schemas.DriverCreate,
    session: SessionDep,
    user_id: UserDep,
) -> schemas.DriverRead:
    driver = Driver(
        created_by_id=user_id,
        updated_by_id=user_id,
        **body.model_dump(),
    )
    session.add(driver)
    await session.flush()
    return schemas.DriverRead.model_validate(driver)


@router.get("/drivers/{driver_id}", response_model=schemas.DriverRead, dependencies=[Depends(require_permission("view", "drivers"))])
async def get_driver(driver_id: int, session: SessionDep) -> schemas.DriverRead:
    driver = await session.get(Driver, driver_id)
    if driver is None:
        raise NotFoundError("Водитель не найден")
    return schemas.DriverRead.model_validate(driver)


@router.patch("/drivers/{driver_id}", response_model=schemas.DriverRead, dependencies=[Depends(require_permission("update", "drivers"))])
async def update_driver(
    driver_id: int,
    body: schemas.DriverCreate,
    session: SessionDep,
    user_id: UserDep,
) -> schemas.DriverRead:
    driver = await session.get(Driver, driver_id)
    if driver is None:
        raise NotFoundError("Водитель не найден")
    for field, value in body.model_dump(exclude_unset=True).items():
        setattr(driver, field, value)
    driver.updated_by_id = user_id
    await session.flush()
    return schemas.DriverRead.model_validate(driver)


@router.delete("/drivers/{driver_id}", status_code=status.HTTP_204_NO_CONTENT, dependencies=[Depends(require_permission("delete", "drivers"))])
async def delete_driver(driver_id: int, session: SessionDep, user_id: UserDep) -> None:
    driver = await session.get(Driver, driver_id)
    if driver is None:
        raise NotFoundError("Водитель не найден")
    driver.soft_delete(user_id)
    await session.flush()


# ========== Автомобили ==========


@router.get("/vehicles", response_model=list[schemas.VehicleRead], dependencies=[Depends(require_permission("view", "vehicles"))])
async def list_vehicles(session: SessionDep) -> list[schemas.VehicleRead]:
    rows = list(
        await session.scalars(select(Vehicle).where())
    )
    return [schemas.VehicleRead.model_validate(r) for r in rows]


@router.post(
    "/vehicles", response_model=schemas.VehicleRead, status_code=status.HTTP_201_CREATED
)
async def create_vehicle(
    body: schemas.VehicleCreate,
    session: SessionDep,
    user_id: UserDep,
) -> schemas.VehicleRead:
    vehicle = Vehicle(
        created_by_id=user_id,
        updated_by_id=user_id,
        **body.model_dump(),
    )
    session.add(vehicle)
    await session.flush()
    return schemas.VehicleRead.model_validate(vehicle)


@router.get("/vehicles/{vehicle_id}", response_model=schemas.VehicleRead, dependencies=[Depends(require_permission("view", "vehicles"))])
async def get_vehicle(vehicle_id: int, session: SessionDep) -> schemas.VehicleRead:
    vehicle = await session.get(Vehicle, vehicle_id)
    if vehicle is None:
        raise NotFoundError("Автомобиль не найден")
    return schemas.VehicleRead.model_validate(vehicle)


@router.patch("/vehicles/{vehicle_id}", response_model=schemas.VehicleRead, dependencies=[Depends(require_permission("update", "vehicles"))])
async def update_vehicle(
    vehicle_id: int,
    body: schemas.VehicleCreate,
    session: SessionDep,
    user_id: UserDep,
) -> schemas.VehicleRead:
    vehicle = await session.get(Vehicle, vehicle_id)
    if vehicle is None:
        raise NotFoundError("Автомобиль не найден")
    for field, value in body.model_dump(exclude_unset=True).items():
        setattr(vehicle, field, value)
    vehicle.updated_by_id = user_id
    await session.flush()
    return schemas.VehicleRead.model_validate(vehicle)


@router.delete("/vehicles/{vehicle_id}", status_code=status.HTTP_204_NO_CONTENT, dependencies=[Depends(require_permission("delete", "vehicles"))])
async def delete_vehicle(
    vehicle_id: int, session: SessionDep, user_id: UserDep
) -> None:
    vehicle = await session.get(Vehicle, vehicle_id)
    if vehicle is None:
        raise NotFoundError("Автомобиль не найден")
    vehicle.soft_delete(user_id)
    await session.flush()


# ========== Маршруты ==========


@router.get("/routes", response_model=list[schemas.RouteRead], dependencies=[Depends(require_permission("view", "routes"))])
async def list_routes(session: SessionDep) -> list[schemas.RouteRead]:
    rows = list(await session.scalars(select(Route).where()))
    return [schemas.RouteRead.model_validate(r) for r in rows]


@router.post(
    "/routes", response_model=schemas.RouteRead, status_code=status.HTTP_201_CREATED
)
async def create_route(
    body: schemas.RouteCreate,
    session: SessionDep,
    user_id: UserDep,
) -> schemas.RouteRead:
    route = Route(
        created_by_id=user_id,
        updated_by_id=user_id,
        **body.model_dump(),
    )
    session.add(route)
    await session.flush()
    return schemas.RouteRead.model_validate(route)


@router.get("/routes/{route_id}", response_model=schemas.RouteRead, dependencies=[Depends(require_permission("view", "routes"))])
async def get_route(route_id: int, session: SessionDep) -> schemas.RouteRead:
    route = await session.get(Route, route_id)
    if route is None:
        raise NotFoundError("Маршрут не найден")
    return schemas.RouteRead.model_validate(route)


@router.patch("/routes/{route_id}", response_model=schemas.RouteRead, dependencies=[Depends(require_permission("update", "routes"))])
async def update_route(
    route_id: int,
    body: schemas.RouteCreate,
    session: SessionDep,
    user_id: UserDep,
) -> schemas.RouteRead:
    route = await session.get(Route, route_id)
    if route is None:
        raise NotFoundError("Маршрут не найден")
    for field, value in body.model_dump(exclude_unset=True).items():
        setattr(route, field, value)
    route.updated_by_id = user_id
    await session.flush()
    return schemas.RouteRead.model_validate(route)


@router.delete("/routes/{route_id}", status_code=status.HTTP_204_NO_CONTENT, dependencies=[Depends(require_permission("delete", "routes"))])
async def delete_route(route_id: int, session: SessionDep, user_id: UserDep) -> None:
    route = await session.get(Route, route_id)
    if route is None:
        raise NotFoundError("Маршрут не найден")
    route.soft_delete(user_id)
    await session.flush()
