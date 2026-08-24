"""API для LPN."""

from __future__ import annotations

from fastapi import APIRouter, Depends, status

from app.api.deps import Services, UserDep, require_permission
from app.api.v1.warehouse.schemas import LPNCreate, LPNRead
from app.core.exceptions import NotFoundError

router = APIRouter(prefix="/warehouse", tags=["warehouse-lpns"])


@router.get("/lpns", response_model=list[LPNRead], dependencies=[Depends(require_permission("view", "lpns"))])
async def list_lpns(services: Services) -> list[LPNRead]:
    rows = await services.lpn.list_all()
    return [LPNRead.model_validate(r) for r in rows]


@router.post("/lpns", response_model=LPNRead, status_code=status.HTTP_201_CREATED, dependencies=[Depends(require_permission("create", "lpns"))])
async def create_lpn(body: LPNCreate, services: Services, user_id: UserDep) -> LPNRead:
    row = await services.lpn.create(user_id=user_id, status=body.status)
    return LPNRead.model_validate(row)


@router.get("/lpns/{lpn_id}", response_model=LPNRead, dependencies=[Depends(require_permission("view", "lpns"))])
async def get_lpn(lpn_id: int, services: Services) -> LPNRead:
    lpn = await services.lpn.get_by_id(lpn_id)
    if lpn is None:
        raise NotFoundError("LPN не найдена")
    return LPNRead.model_validate(lpn)


@router.patch("/lpns/{lpn_id}", response_model=LPNRead, dependencies=[Depends(require_permission("update", "lpns"))])
async def update_lpn(lpn_id: int, body: LPNCreate, services: Services, user_id: UserDep) -> LPNRead:
    lpn = await services.lpn.update(lpn_id, user_id=user_id, status=body.status)
    if lpn is None:
        raise NotFoundError("LPN не найдена")
    return LPNRead.model_validate(lpn)


@router.delete("/lpns/{lpn_id}", status_code=status.HTTP_204_NO_CONTENT, dependencies=[Depends(require_permission("delete", "lpns"))])
async def delete_lpn(lpn_id: int, services: Services, user_id: UserDep) -> None:
    ok = await services.lpn.soft_delete(lpn_id, user_id)
    if not ok:
        raise NotFoundError("LPN не найдена")
