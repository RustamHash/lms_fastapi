# app/api/v1/parties/routes/clients.py

"""Роутер для клиентов."""

from __future__ import annotations

from fastapi import APIRouter, Depends, status

from app.api.deps import SessionDep, require_permission
from app.api.v1.parties.schemas import ClientCreate, ClientRead, ClientUpdate
from app.core.exceptions import NotFoundError
from app.parties.repository import ClientRepository
from app.parties.services.client_service import ClientService

router = APIRouter(prefix="/clients", tags=["clients"])


def get_service(session: SessionDep) -> ClientService:
    return ClientService(ClientRepository(session))


@router.get("", response_model=list[ClientRead], dependencies=[Depends(require_permission("view", "clients"))])
async def list_clients(service: ClientService = Depends(get_service)) -> list[ClientRead]:
    return await service.list_all()


@router.post("", response_model=ClientRead, status_code=status.HTTP_201_CREATED, dependencies=[Depends(require_permission("create", "clients"))])
async def create_client(body: ClientCreate, service: ClientService = Depends(get_service)) -> ClientRead:
    return await service.create(**body.model_dump())


@router.get("/{id}", response_model=ClientRead, dependencies=[Depends(require_permission("view", "clients"))])
async def get_client(id: int, service: ClientService = Depends(get_service)) -> ClientRead:
    row = await service.get_by_id(id)
    if row is None:
        raise NotFoundError("Клиент не найден")
    return row


@router.patch("/{id}", response_model=ClientRead, dependencies=[Depends(require_permission("update", "clients"))])
async def update_client(id: int, body: ClientUpdate, service: ClientService = Depends(get_service)) -> ClientRead:
    row = await service.update(id, **body.model_dump(exclude_unset=True))
    if row is None:
        raise NotFoundError("Клиент не найден")
    return row


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT, dependencies=[Depends(require_permission("delete", "clients"))])
async def delete_client(id: int, service: ClientService = Depends(get_service)) -> None:
    ok = await service.soft_delete(id)
    if not ok:
        raise NotFoundError("Клиент не найден")
