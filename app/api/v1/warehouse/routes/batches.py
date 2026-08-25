"""API для партий."""

from __future__ import annotations

from fastapi import APIRouter, Depends, status

from app.api.deps import UserDep, require_permission
from app.api.v1.warehouse.deps import get_batch_service
from app.api.v1.warehouse.schemas import BatchCreate, BatchRead
from app.core.exceptions import ConflictError, NotFoundError
from app.warehouse.services.batch_service import BatchService

router = APIRouter(prefix="/warehouse", tags=["warehouse-batches"])


@router.get("/batches", response_model=list[BatchRead], dependencies=[Depends(require_permission("view", "batches"))])
async def list_batches(
    service: BatchService = Depends(get_batch_service),
    product_id: int | None = None,
) -> list[BatchRead]:
    if product_id:
        rows = await service.list_by_product(product_id)
    else:
        rows = await service.list_all()
    return [BatchRead.model_validate(r) for r in rows]


@router.post("/batches", response_model=BatchRead, status_code=status.HTTP_201_CREATED, dependencies=[Depends(require_permission("create", "batches"))])
async def create_batch(
    body: BatchCreate,
    user_id: UserDep,
    service: BatchService = Depends(get_batch_service),
) -> BatchRead:
    try:
        row = await service.create(user_id=user_id, **body.model_dump())
    except ValueError as e:
        raise ConflictError(str(e)) from e
    return BatchRead.model_validate(row)


@router.get("/batches/{batch_id}", response_model=BatchRead, dependencies=[Depends(require_permission("view", "batches"))])
async def get_batch(
    batch_id: int,
    service: BatchService = Depends(get_batch_service),
) -> BatchRead:
    batch = await service.get_by_id(batch_id)
    if batch is None:
        raise NotFoundError("Партия не найдена")
    return BatchRead.model_validate(batch)


@router.patch("/batches/{batch_id}", response_model=BatchRead, dependencies=[Depends(require_permission("update", "batches"))])
async def update_batch(
    batch_id: int,
    body: BatchCreate,
    user_id: UserDep,
    service: BatchService = Depends(get_batch_service),
) -> BatchRead:
    batch = await service.update(batch_id, user_id=user_id, **body.model_dump(exclude_unset=True))
    if batch is None:
        raise NotFoundError("Партия не найдена")
    return BatchRead.model_validate(batch)


@router.delete("/batches/{batch_id}", status_code=status.HTTP_204_NO_CONTENT, dependencies=[Depends(require_permission("delete", "batches"))])
async def delete_batch(
    batch_id: int,
    user_id: UserDep,
    service: BatchService = Depends(get_batch_service),
) -> None:
    ok = await service.soft_delete(batch_id, user_id)
    if not ok:
        raise NotFoundError("Партия не найдена")
