"""API для водителей."""

from __future__ import annotations

from fastapi import APIRouter, Depends, status

from app.api.deps import Services, UserDep, require_permission
from app.api.v1.delivery.schemas import DriverCreate, DriverRead
from app.core.exceptions import NotFoundError
from app.delivery.repository import DriverRepository

router = APIRouter(prefix="/delivery/drivers", tags=["delivery-drivers"])


@router.get("", response_model=list[DriverRead], dependencies=[Depends(require_permission("view", "drivers"))])
async def list_drivers(services: Services) -> list[DriverRead]:
    rows = await DriverRepository(services.session).list_all()
    return [DriverRead.model_validate(r) for r in rows]


@router.post("", response_model=DriverRead, status_code=status.HTTP_201_CREATED, dependencies=[Depends(require_permission("create", "drivers"))])
async def create_driver(body: DriverCreate, services: Services, user_id: UserDep) -> DriverRead:
    driver = await DriverRepository(services.session).create(**body.model_dump())
    return DriverRead.model_validate(driver)


@router.get("/{driver_id}", response_model=DriverRead, dependencies=[Depends(require_permission("view", "drivers"))])
async def get_driver(driver_id: int, services: Services) -> DriverRead:
    driver = await DriverRepository(services.session).get_by_id(driver_id)
    if driver is None:
        raise NotFoundError("Водитель не найден")
    return DriverRead.model_validate(driver)


@router.patch("/{driver_id}", response_model=DriverRead, dependencies=[Depends(require_permission("update", "drivers"))])
async def update_driver(driver_id: int, body: DriverCreate, services: Services, user_id: UserDep) -> DriverRead:
    driver = await DriverRepository(services.session).update(driver_id, **body.model_dump(exclude_unset=True))
    if driver is None:
        raise NotFoundError("Водитель не найден")
    return DriverRead.model_validate(driver)


@router.delete("/{driver_id}", status_code=status.HTTP_204_NO_CONTENT, dependencies=[Depends(require_permission("delete", "drivers"))])
async def delete_driver(driver_id: int, services: Services, user_id: UserDep) -> None:
    ok = await DriverRepository(services.session).soft_delete(driver_id, user_id)
    if not ok:
        raise NotFoundError("Водитель не найден")
