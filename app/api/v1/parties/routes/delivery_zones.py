# app/api/v1/parties/routes/delivery_zones.py

"""Роутер для зон доставки."""

from __future__ import annotations

from fastapi import APIRouter, Depends, status

from app.api.deps import SessionDep, require_permission
from app.api.v1.parties.schemas import DeliveryZoneCreate, DeliveryZoneRead, DeliveryZoneUpdate
from app.core.exceptions import NotFoundError
from app.parties.repository import DeliveryZoneRepository
from app.parties.services.delivery_zone_service import DeliveryZoneService

router = APIRouter(prefix="/delivery-zones", tags=["delivery-zones"])


def get_service(session: SessionDep) -> DeliveryZoneService:
    return DeliveryZoneService(DeliveryZoneRepository(session))


@router.get("", response_model=list[DeliveryZoneRead], dependencies=[Depends(require_permission("view", "addresses"))])
async def list_delivery_zones(service: DeliveryZoneService = Depends(get_service)) -> list[DeliveryZoneRead]:
    return await service.list_all()


@router.post("", response_model=DeliveryZoneRead, status_code=status.HTTP_201_CREATED, dependencies=[Depends(require_permission("create", "addresses"))])
async def create_delivery_zone(body: DeliveryZoneCreate, service: DeliveryZoneService = Depends(get_service)) -> DeliveryZoneRead:
    return await service.create(**body.model_dump())


@router.get("/{id}", response_model=DeliveryZoneRead, dependencies=[Depends(require_permission("view", "addresses"))])
async def get_delivery_zone(id: int, service: DeliveryZoneService = Depends(get_service)) -> DeliveryZoneRead:
    row = await service.get_by_id(id)
    if row is None:
        raise NotFoundError("Зона доставки не найдена")
    return row


@router.patch("/{id}", response_model=DeliveryZoneRead, dependencies=[Depends(require_permission("update", "addresses"))])
async def update_delivery_zone(id: int, body: DeliveryZoneUpdate, service: DeliveryZoneService = Depends(get_service)) -> DeliveryZoneRead:
    row = await service.update(id, **body.model_dump(exclude_unset=True))
    if row is None:
        raise NotFoundError("Зона доставки не найдена")
    return row


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT, dependencies=[Depends(require_permission("delete", "addresses"))])
async def delete_delivery_zone(id: int, service: DeliveryZoneService = Depends(get_service)) -> None:
    ok = await service.soft_delete(id)
    if not ok:
        raise NotFoundError("Зона доставки не найдена")
