# app/api/v1/parties/routes/carriers.py

"""Роутер для перевозчиков."""

from __future__ import annotations

from fastapi import APIRouter, Depends, status

from app.api.deps import SessionDep, require_permission
from app.api.v1.parties.schemas import CarrierCreate, CarrierRead, CarrierUpdate
from app.core.exceptions import NotFoundError
from app.parties.repository import CarrierRepository
from app.parties.services.carrier_service import CarrierService

router = APIRouter(prefix="/carriers", tags=["carriers"])


def get_service(session: SessionDep) -> CarrierService:
    return CarrierService(CarrierRepository(session))


@router.get("", response_model=list[CarrierRead], dependencies=[Depends(require_permission("view", "carriers"))])
async def list_carriers(service: CarrierService = Depends(get_service)) -> list[CarrierRead]:
    return await service.list_all()


@router.post("", response_model=CarrierRead, status_code=status.HTTP_201_CREATED, dependencies=[Depends(require_permission("create", "carriers"))])
async def create_carrier(body: CarrierCreate, service: CarrierService = Depends(get_service)) -> CarrierRead:
    return await service.create(**body.model_dump())


@router.get("/{id}", response_model=CarrierRead, dependencies=[Depends(require_permission("view", "carriers"))])
async def get_carrier(id: int, service: CarrierService = Depends(get_service)) -> CarrierRead:
    row = await service.get_by_id(id)
    if row is None:
        raise NotFoundError("Перевозчик не найден")
    return row


@router.patch("/{id}", response_model=CarrierRead, dependencies=[Depends(require_permission("update", "carriers"))])
async def update_carrier(id: int, body: CarrierUpdate, service: CarrierService = Depends(get_service)) -> CarrierRead:
    row = await service.update(id, **body.model_dump(exclude_unset=True))
    if row is None:
        raise NotFoundError("Перевозчик не найден")
    return row


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT, dependencies=[Depends(require_permission("delete", "carriers"))])
async def delete_carrier(id: int, service: CarrierService = Depends(get_service)) -> None:
    ok = await service.soft_delete(id)
    if not ok:
        raise NotFoundError("Перевозчик не найден")
