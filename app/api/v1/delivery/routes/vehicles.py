"""API для автомобилей."""

from __future__ import annotations

from fastapi import APIRouter, Depends, status

from app.api.deps import Services, UserDep, require_permission
from app.api.v1.delivery.schemas import VehicleCreate, VehicleRead
from app.core.exceptions import NotFoundError
from app.delivery.repository import VehicleRepository

router = APIRouter(prefix="/delivery/vehicles", tags=["delivery-vehicles"])


@router.get("", response_model=list[VehicleRead], dependencies=[Depends(require_permission("view", "vehicles"))])
async def list_vehicles(services: Services) -> list[VehicleRead]:
    rows = await VehicleRepository(services.session).list_all()
    return [VehicleRead.model_validate(r) for r in rows]


@router.post("", response_model=VehicleRead, status_code=status.HTTP_201_CREATED, dependencies=[Depends(require_permission("create", "vehicles"))])
async def create_vehicle(body: VehicleCreate, services: Services, user_id: UserDep) -> VehicleRead:
    vehicle = await VehicleRepository(services.session).create(**body.model_dump())
    return VehicleRead.model_validate(vehicle)


@router.get("/{vehicle_id}", response_model=VehicleRead, dependencies=[Depends(require_permission("view", "vehicles"))])
async def get_vehicle(vehicle_id: int, services: Services) -> VehicleRead:
    vehicle = await VehicleRepository(services.session).get_by_id(vehicle_id)
    if vehicle is None:
        raise NotFoundError("Автомобиль не найден")
    return VehicleRead.model_validate(vehicle)


@router.patch("/{vehicle_id}", response_model=VehicleRead, dependencies=[Depends(require_permission("update", "vehicles"))])
async def update_vehicle(vehicle_id: int, body: VehicleCreate, services: Services, user_id: UserDep) -> VehicleRead:
    vehicle = await VehicleRepository(services.session).update(vehicle_id, **body.model_dump(exclude_unset=True))
    if vehicle is None:
        raise NotFoundError("Автомобиль не найден")
    return VehicleRead.model_validate(vehicle)


@router.delete("/{vehicle_id}", status_code=status.HTTP_204_NO_CONTENT, dependencies=[Depends(require_permission("delete", "vehicles"))])
async def delete_vehicle(vehicle_id: int, services: Services, user_id: UserDep) -> None:
    ok = await VehicleRepository(services.session).soft_delete(vehicle_id, user_id)
    if not ok:
        raise NotFoundError("Автомобиль не найден")
