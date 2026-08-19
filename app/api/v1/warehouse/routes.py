"""API для модуля warehouse."""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.warehouse import schemas
from app.core.dependencies import get_current_user_id, get_session
from app.warehouse.services import (
    BatchService,
    LPNService,
    PlacementService,
    ProductService,
    StockService,
    TaskService,
)

router = APIRouter(prefix="/warehouse", tags=["warehouse"])

SessionDep = Annotated[AsyncSession, Depends(get_session)]
UserDep = Annotated[int | None, Depends(get_current_user_id)]


# ========== Товары ==========

@router.get("/products", response_model=list[schemas.ProductRead])
async def list_products(
    session: SessionDep,
    depositor_id: int | None = None,
) -> list[schemas.ProductRead]:
    service = ProductService(session)
    if depositor_id:
        rows = await service.list_by_depositor(depositor_id)
    else:
        from sqlalchemy import select
        from app.warehouse.models import Product
        rows = list(await session.scalars(select(Product).where(Product.is_deleted.is_(False))))
    return [schemas.ProductRead.model_validate(r) for r in rows]


@router.post("/products", response_model=schemas.ProductRead, status_code=status.HTTP_201_CREATED)
async def create_product(
    body: schemas.ProductCreate,
    session: SessionDep,
    user_id: UserDep,
) -> schemas.ProductRead:
    service = ProductService(session)
    try:
        row = await service.create(user_id=user_id, **body.model_dump())
    except ValueError as e:
        raise HTTPException(status.HTTP_409_CONFLICT, detail=str(e)) from e
    return schemas.ProductRead.model_validate(row)


@router.patch("/products/{product_id}", response_model=schemas.ProductRead)
async def update_product(
    product_id: int,
    body: schemas.ProductCreate,
    session: SessionDep,
    user_id: UserDep,
) -> schemas.ProductRead:
    from app.warehouse.models import Product
    product = await session.get(Product, product_id)
    if product is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Товар не найден")
    for field, value in body.model_dump(exclude_unset=True).items():
        setattr(product, field, value)
    product.updated_by_id = user_id
    await session.flush()
    return schemas.ProductRead.model_validate(product)


@router.get("/products/{product_id}", response_model=schemas.ProductRead)
async def get_product(product_id: int, session: SessionDep) -> schemas.ProductRead:
    service = ProductService(session)
    product = await service.get_by_id(product_id)
    if product is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Товар не найден")
    return schemas.ProductRead.model_validate(product)


@router.delete("/products/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_product(product_id: int, session: SessionDep, user_id: UserDep) -> None:
    service = ProductService(session)
    ok = await service.soft_delete(product_id, user_id)
    if not ok:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Товар не найден")


# ========== Партии ==========

@router.post("/batches", response_model=schemas.BatchRead, status_code=status.HTTP_201_CREATED)
async def create_batch(
    body: schemas.BatchCreate,
    session: SessionDep,
    user_id: UserDep,
) -> schemas.BatchRead:
    service = BatchService(session)
    try:
        row = await service.create(user_id=user_id, **body.model_dump())
    except ValueError as e:
        raise HTTPException(status.HTTP_409_CONFLICT, detail=str(e)) from e
    return schemas.BatchRead.model_validate(row)


@router.get("/batches", response_model=list[schemas.BatchRead])
async def list_batches(session: SessionDep, product_id: int | None = None) -> list[schemas.BatchRead]:
    service = BatchService(session)
    if product_id:
        rows = await service.list_by_product(product_id)
    else:
        from sqlalchemy import select
        from app.warehouse.models import Batch
        rows = list(await session.scalars(select(Batch).where(Batch.is_deleted.is_(False))))
    return [schemas.BatchRead.model_validate(r) for r in rows]


@router.get("/batches/{batch_id}", response_model=schemas.BatchRead)
async def get_batch(batch_id: int, session: SessionDep) -> schemas.BatchRead:
    service = BatchService(session)
    batch = await service.get_by_id(batch_id)
    if batch is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Партия не найдена")
    return schemas.BatchRead.model_validate(batch)


@router.delete("/batches/{batch_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_batch(batch_id: int, session: SessionDep, user_id: UserDep) -> None:
    from app.warehouse.models import Batch
    batch = await session.get(Batch, batch_id)
    if batch is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Партия не найдена")
    batch.soft_delete(user_id)
    await session.flush()


# ========== LPN ==========

@router.post("/lpns", response_model=schemas.LPNRead, status_code=status.HTTP_201_CREATED)
async def create_lpn(
    body: schemas.LPNCreate,
    session: SessionDep,
    user_id: UserDep,
) -> schemas.LPNRead:
    service = LPNService(session)
    row = await service.create(user_id=user_id, status=body.status)
    return schemas.LPNRead.model_validate(row)


@router.get("/lpns", response_model=list[schemas.LPNRead])
async def list_lpns(session: SessionDep) -> list[schemas.LPNRead]:
    from sqlalchemy import select
    from app.warehouse.models import LPN
    rows = list(await session.scalars(select(LPN).where(LPN.is_deleted.is_(False))))
    return [schemas.LPNRead.model_validate(r) for r in rows]


@router.get("/lpns/{lpn_id}", response_model=schemas.LPNRead)
async def get_lpn(lpn_id: int, session: SessionDep) -> schemas.LPNRead:
    from app.warehouse.models import LPN
    lpn = await session.get(LPN, lpn_id)
    if lpn is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="LPN не найдена")
    return schemas.LPNRead.model_validate(lpn)


@router.delete("/lpns/{lpn_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_lpn(lpn_id: int, session: SessionDep, user_id: UserDep) -> None:
    from app.warehouse.models import LPN
    lpn = await session.get(LPN, lpn_id)
    if lpn is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="LPN не найдена")
    lpn.soft_delete(user_id)
    await session.flush()


# ========== Остатки ==========

@router.post("/stock/add", response_model=schemas.StockBalanceRead)
async def add_stock(
    body: schemas.StockAdd,
    session: SessionDep,
    user_id: UserDep,
) -> schemas.StockBalanceRead:
    service = StockService(session)
    try:
        balance = await service.add_stock(user_id=user_id, **body.model_dump())
    except ValueError as e:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, detail=str(e)) from e
    return schemas.StockBalanceRead.model_validate(balance)


@router.post("/stock/remove", response_model=schemas.StockBalanceRead)
async def remove_stock(
    body: schemas.StockRemove,
    session: SessionDep,
    user_id: UserDep,
) -> schemas.StockBalanceRead:
    service = StockService(session)
    try:
        balance = await service.remove_stock(user_id=user_id, **body.model_dump())
    except ValueError as e:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, detail=str(e)) from e
    return schemas.StockBalanceRead.model_validate(balance)


@router.post("/stock/move", response_model=schemas.StockBalanceRead)
async def move_stock(
    body: schemas.StockMove,
    session: SessionDep,
    user_id: UserDep,
) -> schemas.StockBalanceRead:
    service = StockService(session)
    try:
        balance = await service.move_stock(user_id=user_id, **body.model_dump())
    except ValueError as e:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, detail=str(e)) from e
    return schemas.StockBalanceRead.model_validate(balance)


# ========== Задания ==========

@router.post("/tasks", response_model=schemas.TaskRead, status_code=status.HTTP_201_CREATED)
async def create_task(
    body: schemas.TaskCreate,
    session: SessionDep,
    user_id: UserDep,
) -> schemas.TaskRead:
    service = TaskService(session)
    task = await service.create(user_id=user_id, **body.model_dump())
    return schemas.TaskRead.model_validate(task)


@router.post("/tasks/{task_id}/lines", status_code=status.HTTP_201_CREATED)
async def add_task_line(
    task_id: int,
    body: schemas.TaskLineAdd,
    session: SessionDep,
    user_id: UserDep,
) -> dict:
    service = TaskService(session)
    line = await service.add_line(user_id=user_id, task_id=task_id, **body.model_dump())
    return {"id": line.id}


@router.post("/tasks/{task_id}/start", response_model=schemas.TaskRead)
async def start_task(
    task_id: int,
    session: SessionDep,
    user_id: UserDep,
) -> schemas.TaskRead:
    service = TaskService(session)
    task = await service.start(user_id=user_id, task_id=task_id)
    if task is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Задание не найдено")
    return schemas.TaskRead.model_validate(task)


@router.get("/tasks", response_model=list[schemas.TaskRead])
async def list_tasks(session: SessionDep) -> list[schemas.TaskRead]:
    from sqlalchemy import select
    from app.warehouse.models import Task
    rows = list(await session.scalars(select(Task).where(Task.is_deleted.is_(False))))
    return [schemas.TaskRead.model_validate(r) for r in rows]


@router.get("/tasks/{task_id}", response_model=schemas.TaskRead)
async def get_task(task_id: int, session: SessionDep) -> schemas.TaskRead:
    from app.warehouse.models import Task
    task = await session.get(Task, task_id)
    if task is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Задание не найдено")
    return schemas.TaskRead.model_validate(task)


@router.delete("/tasks/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_task(task_id: int, session: SessionDep, user_id: UserDep) -> None:
    from app.warehouse.models import Task
    task = await session.get(Task, task_id)
    if task is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Задание не найдено")
    task.soft_delete(user_id)
    await session.flush()


@router.post("/task-lines/{line_id}/complete")
async def complete_task_line(
    line_id: int,
    body: schemas.TaskLineComplete,
    session: SessionDep,
    user_id: UserDep,
) -> dict:
    service = TaskService(session)
    try:
        line = await service.complete_line(
            user_id=user_id,
            task_line_id=line_id,
            **body.model_dump(),
        )
    except ValueError as e:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, detail=str(e)) from e
    return {"id": line.id, "fact_qty": line.fact_qty}


@router.post("/tasks/{task_id}/complete", response_model=schemas.TaskRead)
async def complete_task(
    task_id: int,
    body: schemas.TaskComplete,
    session: SessionDep,
    user_id: UserDep,
) -> schemas.TaskRead:
    service = TaskService(session)
    try:
        task = await service.complete(user_id=user_id, task_id=task_id, force=body.force)
    except ValueError as e:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, detail=str(e)) from e
    return schemas.TaskRead.model_validate(task)
