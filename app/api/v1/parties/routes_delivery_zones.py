"""API для зон доставки."""

from __future__ import annotations

from fastapi import APIRouter, Depends, status
from sqlalchemy import select

from app.api.deps import SessionDep, UserDep, require_permission
from app.api.v1.parties.schemas import DeliveryZoneCreate, DeliveryZoneRead
from app.core.exceptions import ConflictError, NotFoundError
from app.parties.models import DeliveryZone
from app.parties.repository import DeliveryZoneRepository

router = APIRouter(prefix="/delivery-zones", tags=["delivery-zones"])


@router.get(
    "",
    response_model=list[DeliveryZoneRead],
    dependencies=[Depends(require_permission("view", "addresses"))],
)
async def list_delivery_zones(session: SessionDep) -> list[DeliveryZoneRead]:
    """Список зон доставки."""
    zones = await DeliveryZoneRepository(session).list_all()
    return [DeliveryZoneRead.model_validate(z) for z in zones]


@router.post(
    "",
    response_model=DeliveryZoneRead,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_permission("create", "addresses"))],
)
async def create_delivery_zone(
    body: DeliveryZoneCreate,
    session: SessionDep,
    user_id: UserDep,
) -> DeliveryZoneRead:
    """Создать зону доставки."""
    existing = await DeliveryZoneRepository(session).get_by_name(body.name)
    if existing:
        raise ConflictError(f"Зона с названием {body.name} уже существует")

    zone = DeliveryZone(
        name=body.name,
    )
    session.add(zone)
    await session.flush()
    return DeliveryZoneRead.model_validate(zone)


@router.get(
    "/{zone_id}",
    response_model=DeliveryZoneRead,
    dependencies=[Depends(require_permission("view", "addresses"))],
)
async def get_delivery_zone(zone_id: int, session: SessionDep) -> DeliveryZoneRead:
    """Получить зону доставки."""
    zone = await DeliveryZoneRepository(session).get_by_id(zone_id)
    if zone is None:
        raise NotFoundError("Зона доставки не найдена")
    return DeliveryZoneRead.model_validate(zone)


@router.patch(
    "/{zone_id}",
    response_model=DeliveryZoneRead,
    dependencies=[Depends(require_permission("update", "addresses"))],
)
async def update_delivery_zone(
    zone_id: int,
    body: DeliveryZoneCreate,
    session: SessionDep,
    user_id: UserDep,
) -> DeliveryZoneRead:
    """Обновить зону доставки."""
    zone = await DeliveryZoneRepository(session).get_by_id(zone_id)
    if zone is None:
        raise NotFoundError("Зона доставки не найдена")
    zone.name = body.name
    zone.updated_by_id = user_id
    await session.flush()
    return DeliveryZoneRead.model_validate(zone)


@router.delete(
    "/{zone_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(require_permission("delete", "addresses"))],
)
async def delete_delivery_zone(zone_id: int, session: SessionDep, user_id: UserDep) -> None:
    """Удалить зону доставки."""
    zone = await DeliveryZoneRepository(session).get_by_id(zone_id)
    if zone is None:
        raise NotFoundError("Зона доставки не найдена")
    zone.soft_delete(user_id)
    await session.flush()
