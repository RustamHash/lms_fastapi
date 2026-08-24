# app/api/v1/parties/routes/addresses.py

"""Роутер для адресов."""

from __future__ import annotations

from fastapi import APIRouter, Depends, status

from app.api.deps import SessionDep, require_permission
from app.api.v1.parties.schemas import AddressCreate, AddressRead, AddressUpdate
from app.core.exceptions import NotFoundError
from app.parties.repository import AddressRepository
from app.parties.services.address_service import AddressService

router = APIRouter(prefix="/addresses", tags=["addresses"])


def get_service(session: SessionDep) -> AddressService:
    return AddressService(AddressRepository(session))


@router.get("", response_model=list[AddressRead], dependencies=[Depends(require_permission("view", "addresses"))])
async def list_addresses(service: AddressService = Depends(get_service)) -> list[AddressRead]:
    return await service.list_all()


@router.post("", response_model=AddressRead, status_code=status.HTTP_201_CREATED, dependencies=[Depends(require_permission("create", "addresses"))])
async def create_address(body: AddressCreate, service: AddressService = Depends(get_service)) -> AddressRead:
    return await service.create(**body.model_dump())


@router.get("/{id}", response_model=AddressRead, dependencies=[Depends(require_permission("view", "addresses"))])
async def get_address(id: int, service: AddressService = Depends(get_service)) -> AddressRead:
    row = await service.get_by_id(id)
    if row is None:
        raise NotFoundError("Адрес не найден")
    return row


@router.patch("/{id}", response_model=AddressRead, dependencies=[Depends(require_permission("update", "addresses"))])
async def update_address(id: int, body: AddressUpdate, service: AddressService = Depends(get_service)) -> AddressRead:
    row = await service.update(id, **body.model_dump(exclude_unset=True))
    if row is None:
        raise NotFoundError("Адрес не найден")
    return row


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT, dependencies=[Depends(require_permission("delete", "addresses"))])
async def delete_address(id: int, service: AddressService = Depends(get_service)) -> None:
    ok = await service.soft_delete(id)
    if not ok:
        raise NotFoundError("Адрес не найден")
