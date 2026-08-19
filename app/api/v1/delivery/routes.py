"""API для модуля delivery."""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.delivery import schemas
from app.core.dependencies import get_current_user_id, get_session
from app.delivery.models import DeliveryOrder, Driver, Route, Vehicle
from app.delivery.services import DeliveryOrderService

router = APIRouter(prefix="/delivery", tags=["delivery"])

SessionDep = Annotated[AsyncSession, Depends(get_session)]
UserDep = Annotated[int | None, Depends(get_current_user_id)]


# ========== Заказы на доставку ==========

@router.get("/orders", response_model=list[schemas.DeliveryOrderRead])
async def list_orders(
    session: SessionDep,
    trade_point_id: int | None = None,
) -> list[schemas.DeliveryOrderRead]:
    service = DeliveryOrderService(session)
    if trade_point_id:
        rows = await service.list_by_trade_point(trade_point_id)
    else:
        rows = await service.list_all()
    return [schemas.DeliveryOrderRead.model_validate(r) for r in rows]


@router.post("/orders", response_model=schemas.DeliveryOrderRead, status_code=status.HTTP_201_CREATED)
async def create_order(
    body: schemas.DeliveryOrderCreate,
    session: SessionDep,
    user_id: UserDep,
) -> schemas.DeliveryOrderRead:
    service = DeliveryOrderService(session)
    order = await service.create(user_id=user_id, **body.model_dump())
    return schemas.DeliveryOrderRead.model_validate(order)


@router.get("/orders/{order_id}", response_model=schemas.DeliveryOrderRead)
async def get_order(order_id: int, session: SessionDep) -> schemas.DeliveryOrderRead:
    service = DeliveryOrderService(session)
    order = await service.get_by_id(order_id)
    if order is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Заказ не найден")
    return schemas.DeliveryOrderRead.model_validate(order)


@router.patch("/orders/{order_id}/status", response_model=schemas.DeliveryOrderRead)
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
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Заказ не найден")
    return schemas.DeliveryOrderRead.model_validate(order)


# ========== Водители ==========

@router.get("/drivers", response_model=list[schemas.DriverRead])
async def list_drivers(session: SessionDep) -> list[schemas.DriverRead]:
    rows = list(await session.scalars(select(Driver).where(Driver.is_deleted.is_(False))))
    return [schemas.DriverRead.model_validate(r) for r in rows]


@router.post("/drivers", response_model=schemas.DriverRead, status_code=status.HTTP_201_CREATED)
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


@router.get("/drivers/{driver_id}", response_model=schemas.DriverRead)
async def get_driver(driver_id: int, session: SessionDep) -> schemas.DriverRead:
    driver = await session.get(Driver, driver_id)
    if driver is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Водитель не найден")
    return schemas.DriverRead.model_validate(driver)


@router.patch("/drivers/{driver_id}", response_model=schemas.DriverRead)
async def update_driver(
    driver_id: int,
    body: schemas.DriverCreate,
    session: SessionDep,
    user_id: UserDep,
) -> schemas.DriverRead:
    driver = await session.get(Driver, driver_id)
    if driver is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Водитель не найден")
    for field, value in body.model_dump(exclude_unset=True).items():
        setattr(driver, field, value)
    driver.updated_by_id = user_id
    await session.flush()
    return schemas.DriverRead.model_validate(driver)


@router.delete("/drivers/{driver_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_driver(driver_id: int, session: SessionDep, user_id: UserDep) -> None:
    driver = await session.get(Driver, driver_id)
    if driver is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Водитель не найден")
    driver.soft_delete(user_id)
    await session.flush()


# ========== Автомобили ==========

@router.get("/vehicles", response_model=list[schemas.VehicleRead])
async def list_vehicles(session: SessionDep) -> list[schemas.VehicleRead]:
    rows = list(await session.scalars(select(Vehicle).where(Vehicle.is_deleted.is_(False))))
    return [schemas.VehicleRead.model_validate(r) for r in rows]


@router.post("/vehicles", response_model=schemas.VehicleRead, status_code=status.HTTP_201_CREATED)
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


@router.get("/vehicles/{vehicle_id}", response_model=schemas.VehicleRead)
async def get_vehicle(vehicle_id: int, session: SessionDep) -> schemas.VehicleRead:
    vehicle = await session.get(Vehicle, vehicle_id)
    if vehicle is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Автомобиль не найден")
    return schemas.VehicleRead.model_validate(vehicle)


@router.patch("/vehicles/{vehicle_id}", response_model=schemas.VehicleRead)
async def update_vehicle(
    vehicle_id: int,
    body: schemas.VehicleCreate,
    session: SessionDep,
    user_id: UserDep,
) -> schemas.VehicleRead:
    vehicle = await session.get(Vehicle, vehicle_id)
    if vehicle is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Автомобиль не найден")
    for field, value in body.model_dump(exclude_unset=True).items():
        setattr(vehicle, field, value)
    vehicle.updated_by_id = user_id
    await session.flush()
    return schemas.VehicleRead.model_validate(vehicle)


@router.delete("/vehicles/{vehicle_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_vehicle(vehicle_id: int, session: SessionDep, user_id: UserDep) -> None:
    vehicle = await session.get(Vehicle, vehicle_id)
    if vehicle is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Автомобиль не найден")
    vehicle.soft_delete(user_id)
    await session.flush()


# ========== Маршруты ==========

@router.get("/routes", response_model=list[schemas.RouteRead])
async def list_routes(session: SessionDep) -> list[schemas.RouteRead]:
    rows = list(await session.scalars(select(Route).where(Route.is_deleted.is_(False))))
    return [schemas.RouteRead.model_validate(r) for r in rows]


@router.post("/routes", response_model=schemas.RouteRead, status_code=status.HTTP_201_CREATED)
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


@router.get("/routes/{route_id}", response_model=schemas.RouteRead)
async def get_route(route_id: int, session: SessionDep) -> schemas.RouteRead:
    route = await session.get(Route, route_id)
    if route is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Маршрут не найден")
    return schemas.RouteRead.model_validate(route)


@router.patch("/routes/{route_id}", response_model=schemas.RouteRead)
async def update_route(
    route_id: int,
    body: schemas.RouteCreate,
    session: SessionDep,
    user_id: UserDep,
) -> schemas.RouteRead:
    route = await session.get(Route, route_id)
    if route is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Маршрут не найден")
    for field, value in body.model_dump(exclude_unset=True).items():
        setattr(route, field, value)
    route.updated_by_id = user_id
    await session.flush()
    return schemas.RouteRead.model_validate(route)


@router.delete("/routes/{route_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_route(route_id: int, session: SessionDep, user_id: UserDep) -> None:
    route = await session.get(Route, route_id)
    if route is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Маршрут не найден")
    route.soft_delete(user_id)
    await session.flush()
