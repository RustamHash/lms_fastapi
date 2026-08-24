# app/api/v1/parties/routes/raw_addresses.py

"""Роутер для сырых адресов (алиасов)."""

from __future__ import annotations

from fastapi import APIRouter, Depends, status

from app.api.deps import SessionDep, require_permission
from app.api.v1.parties.schemas import RawAddressCreate, RawAddressRead, RawAddressUpdate
from app.core.exceptions import NotFoundError
from app.parties.repository import RawAddressRepository
from app.parties.services.raw_address_service import RawAddressService

router = APIRouter(prefix="/aliases", tags=["aliases"])


def get_service(session: SessionDep) -> RawAddressService:
    return RawAddressService(RawAddressRepository(session))


@router.get("", response_model=list[RawAddressRead], dependencies=[Depends(require_permission("view", "addresses"))])
async def list_aliases(service: RawAddressService = Depends(get_service)) -> list[RawAddressRead]:
    return await service.list_all()


@router.post("", response_model=RawAddressRead, status_code=status.HTTP_201_CREATED, dependencies=[Depends(require_permission("create", "addresses"))])
async def create_alias(body: RawAddressCreate, service: RawAddressService = Depends(get_service)) -> RawAddressRead:
    return await service.create(**body.model_dump())


@router.get("/{id}", response_model=RawAddressRead, dependencies=[Depends(require_permission("view", "addresses"))])
async def get_alias(id: int, service: RawAddressService = Depends(get_service)) -> RawAddressRead:
    row = await service.get_by_id(id)
    if row is None:
        raise NotFoundError("Сырой адрес не найден")
    return row


@router.patch("/{id}", response_model=RawAddressRead, dependencies=[Depends(require_permission("update", "addresses"))])
async def update_alias(id: int, body: RawAddressUpdate, service: RawAddressService = Depends(get_service)) -> RawAddressRead:
    row = await service.update(id, **body.model_dump(exclude_unset=True))
    if row is None:
        raise NotFoundError("Сырой адрес не найден")
    return row


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT, dependencies=[Depends(require_permission("delete", "addresses"))])
async def delete_alias(id: int, service: RawAddressService = Depends(get_service)) -> None:
    ok = await service.soft_delete(id)
    if not ok:
        raise NotFoundError("Сырой адрес не найден")
