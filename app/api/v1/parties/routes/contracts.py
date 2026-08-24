# app/api/v1/parties/routes/contracts.py

"""Роутер для договоров."""

from __future__ import annotations

from fastapi import APIRouter, Depends, status

from app.api.deps import SessionDep, require_permission
from app.api.v1.parties.schemas import ContractCreate, ContractRead, ContractUpdate
from app.core.exceptions import NotFoundError
from app.parties.repository import ContractRepository
from app.parties.services.contract_service import ContractService

router = APIRouter(prefix="/contracts", tags=["contracts"])


def get_service(session: SessionDep) -> ContractService:
    return ContractService(ContractRepository(session))


@router.get("", response_model=list[ContractRead], dependencies=[Depends(require_permission("view", "contracts"))])
async def list_contracts(service: ContractService = Depends(get_service)) -> list[ContractRead]:
    return await service.list_all()


@router.post("", response_model=ContractRead, status_code=status.HTTP_201_CREATED, dependencies=[Depends(require_permission("create", "contracts"))])
async def create_contract(body: ContractCreate, service: ContractService = Depends(get_service)) -> ContractRead:
    return await service.create(**body.model_dump())


@router.get("/{id}", response_model=ContractRead, dependencies=[Depends(require_permission("view", "contracts"))])
async def get_contract(id: int, service: ContractService = Depends(get_service)) -> ContractRead:
    row = await service.get_by_id(id)
    if row is None:
        raise NotFoundError("Договор не найден")
    return row


@router.patch("/{id}", response_model=ContractRead, dependencies=[Depends(require_permission("update", "contracts"))])
async def update_contract(id: int, body: ContractUpdate, service: ContractService = Depends(get_service)) -> ContractRead:
    row = await service.update(id, **body.model_dump(exclude_unset=True))
    if row is None:
        raise NotFoundError("Договор не найден")
    return row


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT, dependencies=[Depends(require_permission("delete", "contracts"))])
async def delete_contract(id: int, service: ContractService = Depends(get_service)) -> None:
    ok = await service.soft_delete(id)
    if not ok:
        raise NotFoundError("Договор не найден")
