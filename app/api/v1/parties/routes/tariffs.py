# app/api/v1/parties/routes/tariffs.py

"""Роутер для тарифов."""

from __future__ import annotations

from fastapi import APIRouter, Depends, status

from app.api.deps import SessionDep, require_permission
from app.api.v1.parties.schemas import TariffCreate, TariffRead, TariffUpdate
from app.core.exceptions import NotFoundError
from app.parties.repository import TariffRepository
from app.parties.services.tariff_service import TariffService

router = APIRouter(prefix="/tariffs", tags=["tariffs"])


def get_service(session: SessionDep) -> TariffService:
    return TariffService(TariffRepository(session))


@router.get("", response_model=list[TariffRead], dependencies=[Depends(require_permission("view", "tariffs"))])
async def list_tariffs(service: TariffService = Depends(get_service)) -> list[TariffRead]:
    return await service.list_all()


@router.post("", response_model=TariffRead, status_code=status.HTTP_201_CREATED, dependencies=[Depends(require_permission("create", "tariffs"))])
async def create_tariff(body: TariffCreate, service: TariffService = Depends(get_service)) -> TariffRead:
    return await service.create(**body.model_dump())


@router.get("/{id}", response_model=TariffRead, dependencies=[Depends(require_permission("view", "tariffs"))])
async def get_tariff(id: int, service: TariffService = Depends(get_service)) -> TariffRead:
    row = await service.get_by_id(id)
    if row is None:
        raise NotFoundError("Тариф не найден")
    return row


@router.patch("/{id}", response_model=TariffRead, dependencies=[Depends(require_permission("update", "tariffs"))])
async def update_tariff(id: int, body: TariffUpdate, service: TariffService = Depends(get_service)) -> TariffRead:
    row = await service.update(id, **body.model_dump(exclude_unset=True))
    if row is None:
        raise NotFoundError("Тариф не найден")
    return row


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT, dependencies=[Depends(require_permission("delete", "tariffs"))])
async def delete_tariff(id: int, service: TariffService = Depends(get_service)) -> None:
    ok = await service.soft_delete(id)
    if not ok:
        raise NotFoundError("Тариф не найден")
