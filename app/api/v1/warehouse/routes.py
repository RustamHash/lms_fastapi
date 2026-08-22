"""API для модуля warehouse."""

from __future__ import annotations

from typing import Annotated

from pydantic import BaseModel
from fastapi import HTTPException, APIRouter, Depends, status
from sqlalchemy import select

from app.api.deps import SessionDep, UserDep, require_permission
from app.api.v1.warehouse import schemas
from app.core.exceptions import BadRequestError, ConflictError, NotFoundError
from app.core.statuses import TaskStatus
from app.warehouse.models import Batch, LPN, Product, Task
from app.warehouse.repository import (
    BatchRepository,
    LPNRepository,
    ProductRepository,
    StockRepository,
    TaskLineRepository,
    TaskRepository,
)
from app.warehouse.services import (
    BatchService,
    LPNService,
    PlacementService,
    ProductService,
    StockService,
    TaskService,
)

router = APIRouter(prefix="/warehouse", tags=["warehouse"])


# ========== Товары ==========

@router.get("/products", response_model=list[schemas.ProductRead], dependencies=[Depends(require_permission("view", "products"))])
async def list_products(
    session: SessionDep,
    depositor_id: int | None = None,
) -> list[schemas.ProductRead]:
    service = ProductService(ProductRepository(session))
    if depositor_id:
        rows = await service.list_by_depositor(depositor_id)
    else:
        repo = ProductRepository(session)
    rows = await repo.list_all()
    return [schemas.ProductRead.model_validate(r) for r in rows]


@router.post("/products", response_model=schemas.ProductRead, status_code=status.HTTP_201_CREATED, dependencies=[Depends(require_permission("create", "products"))])
async def create_product(
    body: schemas.ProductCreate,
    session: SessionDep,
    user_id: UserDep,
) -> schemas.ProductRead:
    service = ProductService(ProductRepository(session))
    try:
        row = await service.create(user_id=user_id, **body.model_dump())
    except ValueError as e:
        raise ConflictError(str(e)) from e
    return schemas.ProductRead.model_validate(row)


@router.patch("/products/{product_id}", response_model=schemas.ProductRead, dependencies=[Depends(require_permission("update", "products"))])
async def update_product(
    product_id: int,
    body: schemas.ProductCreate,
    session: SessionDep,
    user_id: UserDep,
) -> schemas.ProductRead:
    product = await ProductRepository(session).get_by_id(product_id)
    if product is None:
        raise NotFoundError("Товар не найден")
    for field, value in body.model_dump(exclude_unset=True).items():
        setattr(product, field, value)
    product.updated_by_id = user_id
    try:
        await session.flush()
    except Exception as e:
        await session.rollback()
        raise HTTPException(status_code=500, detail=f"Ошибка базы данных: {e}")
    return schemas.ProductRead.model_validate(product)


@router.get("/products/{product_id}", response_model=schemas.ProductRead, dependencies=[Depends(require_permission("view", "products"))])
async def get_product(product_id: int, session: SessionDep) -> schemas.ProductRead:
    service = ProductService(ProductRepository(session))
    product = await service.get_by_id(product_id)
    if product is None:
        raise NotFoundError("Товар не найден")
    return schemas.ProductRead.model_validate(product)


@router.delete("/products/{product_id}", status_code=status.HTTP_204_NO_CONTENT, dependencies=[Depends(require_permission("delete", "products"))])
async def delete_product(product_id: int, session: SessionDep, user_id: UserDep) -> None:
    service = ProductService(ProductRepository(session))
    ok = await service.soft_delete(product_id, user_id)
    if not ok:
        raise NotFoundError("Товар не найден")


# ========== Партии ==========

@router.post("/batches", response_model=schemas.BatchRead, status_code=status.HTTP_201_CREATED, dependencies=[Depends(require_permission("create", "batches"))])
async def create_batch(
    body: schemas.BatchCreate,
    session: SessionDep,
    user_id: UserDep,
) -> schemas.BatchRead:
    service = BatchService(BatchRepository(session))
    try:
        row = await service.create(user_id=user_id, **body.model_dump())
    except ValueError as e:
        raise ConflictError(str(e)) from e
    return schemas.BatchRead.model_validate(row)


@router.get("/batches", response_model=list[schemas.BatchRead], dependencies=[Depends(require_permission("view", "batches"))])
async def list_batches(session: SessionDep, product_id: int | None = None) -> list[schemas.BatchRead]:
    service = BatchService(BatchRepository(session))
    if product_id:
        rows = await service.list_by_product(product_id)
    else:
        repo = BatchRepository(session)
    rows = await repo.list_all()
    return [schemas.BatchRead.model_validate(r) for r in rows]


@router.patch(
    "/batches/{batch_id}",
    response_model=schemas.BatchRead,
    dependencies=[Depends(require_permission("update", "batches"))],
)
async def update_batch(
    batch_id: int,
    body: schemas.BatchCreate,
    session: SessionDep,
    user_id: UserDep,
) -> schemas.BatchRead:
    batch = await BatchRepository(session).get_by_id(batch_id)
    if batch is None:
        raise NotFoundError("Партия не найдена")
    for field, value in body.model_dump(exclude_unset=True).items():
        setattr(batch, field, value)
    batch.updated_by_id = user_id
    try:
        await session.flush()
    except Exception as e:
        await session.rollback()
        raise HTTPException(status_code=500, detail=f"Ошибка базы данных: {e}")
    return schemas.BatchRead.model_validate(batch)


@router.get("/batches/{batch_id}", response_model=schemas.BatchRead, dependencies=[Depends(require_permission("view", "batches"))])
async def get_batch(batch_id: int, session: SessionDep) -> schemas.BatchRead:
    service = BatchService(BatchRepository(session))
    batch = await service.get_by_id(batch_id)
    if batch is None:
        raise NotFoundError("Партия не найдена")
    return schemas.BatchRead.model_validate(batch)


@router.delete("/batches/{batch_id}", status_code=status.HTTP_204_NO_CONTENT, dependencies=[Depends(require_permission("delete", "batches"))])
async def delete_batch(batch_id: int, session: SessionDep, user_id: UserDep) -> None:
    batch = await BatchRepository(session).get_by_id(batch_id)
    if batch is None:
        raise NotFoundError("Партия не найдена")
    batch.soft_delete(user_id)
    try:
        await session.flush()
    except Exception as e:
        await session.rollback()
        raise HTTPException(status_code=500, detail=f"Ошибка базы данных: {e}")


# ========== LPN ==========

@router.post("/lpns", response_model=schemas.LPNRead, status_code=status.HTTP_201_CREATED, dependencies=[Depends(require_permission("create", "lpns"))])
async def create_lpn(
    body: schemas.LPNCreate,
    session: SessionDep,
    user_id: UserDep,
) -> schemas.LPNRead:
    service = LPNService(LPNRepository(session))
    row = await service.create(user_id=user_id, status=body.status)
    return schemas.LPNRead.model_validate(row)


@router.get("/lpns", response_model=list[schemas.LPNRead], dependencies=[Depends(require_permission("view", "lpns"))])
async def list_lpns(session: SessionDep,
) -> list[schemas.LPNRead]:
    repo = LPNRepository(session)
    rows = await repo.list_all()
    return [schemas.LPNRead.model_validate(r) for r in rows]


@router.patch(
    "/lpns/{lpn_id}",
    response_model=schemas.LPNRead,
    dependencies=[Depends(require_permission("update", "lpns"))],
)
async def update_lpn(
    lpn_id: int,
    body: schemas.LPNCreate,
    session: SessionDep,
    user_id: UserDep,
) -> schemas.LPNRead:
    lpn = await LPNRepository(session).get_by_id(lpn_id)
    if lpn is None:
        raise NotFoundError("LPN не найдена")
    lpn.status = body.status
    lpn.updated_by_id = user_id
    try:
        await session.flush()
    except Exception as e:
        await session.rollback()
        raise HTTPException(status_code=500, detail=f"Ошибка базы данных: {e}")
    return schemas.LPNRead.model_validate(lpn)


@router.get("/lpns/{lpn_id}", response_model=schemas.LPNRead, dependencies=[Depends(require_permission("view", "lpns"))])
async def get_lpn(lpn_id: int, session: SessionDep) -> schemas.LPNRead:
    lpn = await LPNRepository(session).get_by_id(lpn_id)
    if lpn is None:
        raise NotFoundError("LPN не найдена")
    return schemas.LPNRead.model_validate(lpn)


@router.delete("/lpns/{lpn_id}", status_code=status.HTTP_204_NO_CONTENT, dependencies=[Depends(require_permission("delete", "lpns"))])
async def delete_lpn(lpn_id: int, session: SessionDep, user_id: UserDep) -> None:
    lpn = await LPNRepository(session).get_by_id(lpn_id)
    if lpn is None:
        raise NotFoundError("LPN не найдена")
    lpn.soft_delete(user_id)
    try:
        await session.flush()
    except Exception as e:
        await session.rollback()
        raise HTTPException(status_code=500, detail=f"Ошибка базы данных: {e}")


# ========== Остатки ==========

@router.get(
    "/stock",
    dependencies=[Depends(require_permission("view", "stock"))],
)
async def list_stock(
    session: SessionDep,
    product_id: int | None = None,
    location_id: int | None = None,
):
    from sqlalchemy import select as sa_select
    from app.warehouse.models import StockBalance

    rows = await StockRepository(session).list_balances()
    return [schemas.StockBalanceRead.model_validate(r) for r in rows]


@router.patch("/stock/{stock_id}", response_model=schemas.StockBalanceRead, dependencies=[Depends(require_permission("update", "stock"))])
async def update_stock_balance(
    stock_id: int,
    body: dict,
    session: SessionDep,
    user_id: UserDep,
) -> schemas.StockBalanceRead:
    """Обновить остаток."""
    stock = await StockRepository(session).get_balance_by_id(stock_id)
    if stock is None:
        raise NotFoundError("Остаток не найден")
    if "quantity" in body:
        stock.quantity = body["quantity"]
    if "reserved_quantity" in body:
        stock.reserved_quantity = body["reserved_quantity"]
    stock.updated_by_id = user_id
    try:
        await session.flush()
    except Exception as e:
        await session.rollback()
        raise HTTPException(status_code=500, detail=f"Ошибка базы данных: {e}")
    return schemas.StockBalanceRead.model_validate(stock)


@router.get(
    "/stock/{stock_id}",
    response_model=schemas.StockBalanceRead,
    dependencies=[Depends(require_permission("view", "stock"))],
)
async def get_stock(
    stock_id: int,
    session: SessionDep,
) -> schemas.StockBalanceRead:
    from app.warehouse.models import StockBalance
    stock = await StockRepository(session).get_balance_by_id(stock_id)
    if stock is None:
        raise NotFoundError("Остаток не найден")
    return schemas.StockBalanceRead.model_validate(stock)


@router.post("/stock/clear", status_code=status.HTTP_204_NO_CONTENT, dependencies=[Depends(require_permission("delete", "stock"))])
async def clear_stock(
    body: dict,
    session: SessionDep,
    user_id: UserDep,
) -> None:
    """Обнулить остаток товара в ячейке."""
    service = StockService(StockRepository(session))
    try:
        await service.remove_stock(
            user_id=user_id,
            product_id=body["product_id"],
            location_id=body["location_id"],
            quantity=body.get("quantity", 0),
            lpn_id=body.get("lpn_id"),
            batch_id=body.get("batch_id"),
        )
    except ValueError as e:
        raise BadRequestError(str(e)) from e


@router.post("/stock/add", response_model=schemas.StockBalanceRead, dependencies=[Depends(require_permission("create", "stock"))])
async def add_stock(
    body: schemas.StockAdd,
    session: SessionDep,
    user_id: UserDep,
) -> schemas.StockBalanceRead:
    service = StockService(StockRepository(session))
    try:
        balance = await service.add_stock(user_id=user_id, **body.model_dump())
    except ValueError as e:
        raise BadRequestError(str(e)) from e
    return schemas.StockBalanceRead.model_validate(balance)


@router.delete("/stock/{stock_id}", status_code=status.HTTP_204_NO_CONTENT, dependencies=[Depends(require_permission("delete", "stock"))])
async def delete_stock_balance(
    stock_id: int,
    session: SessionDep,
    user_id: UserDep,
) -> None:
    """Удалить запись остатка."""
    stock = await StockRepository(session).get_balance_by_id(stock_id)
    if stock is None:
        raise NotFoundError("Остаток не найден")
    stock.soft_delete(user_id)
    try:
        await session.flush()
    except Exception as e:
        await session.rollback()
        raise HTTPException(status_code=500, detail=f"Ошибка базы данных: {e}")


@router.post("/stock/remove", response_model=schemas.StockBalanceRead, dependencies=[Depends(require_permission("delete", "stock"))])
async def remove_stock(
    body: schemas.StockRemove,
    session: SessionDep,
    user_id: UserDep,
) -> schemas.StockBalanceRead:
    service = StockService(StockRepository(session))
    try:
        balance = await service.remove_stock(user_id=user_id, **body.model_dump())
    except ValueError as e:
        raise BadRequestError(str(e)) from e
    return schemas.StockBalanceRead.model_validate(balance)


@router.post("/stock/move", response_model=schemas.StockBalanceRead, dependencies=[Depends(require_permission("update", "stock"))])
async def move_stock(
    body: schemas.StockMove,
    session: SessionDep,
    user_id: UserDep,
) -> schemas.StockBalanceRead:
    service = StockService(StockRepository(session))
    try:
        balance = await service.move_stock(user_id=user_id, **body.model_dump())
    except ValueError as e:
        raise BadRequestError(str(e)) from e
    return schemas.StockBalanceRead.model_validate(balance)


# ========== Задания ==========

@router.post("/tasks", response_model=schemas.TaskRead, status_code=status.HTTP_201_CREATED, dependencies=[Depends(require_permission("create", "tasks"))])
async def create_task(
    body: schemas.TaskCreate,
    session: SessionDep,
    user_id: UserDep,
) -> schemas.TaskRead:
    service = TaskService(TaskRepository(session), TaskLineRepository(session), StockService(StockRepository(session)))
    task = await service.create(user_id=user_id, **body.model_dump())
    return schemas.TaskRead.model_validate(task)


@router.post(
    "/tasks/from-document",
    response_model=schemas.TaskRead,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_permission("create", "tasks"))],
)
async def create_task_from_document(
    body: dict,
    session: SessionDep,
    user_id: UserDep,
) -> schemas.TaskRead:
    service = TaskService(TaskRepository(session), TaskLineRepository(session), StockService(StockRepository(session)))
    try:
        task = await service.create_from_document(
            user_id=user_id,
            document_id=body.document_id,
            task_type=body["task_type"],
            assignee_id=body.assignee_id,
            warehouse_id=body.warehouse_id,
        )
    except ValueError as e:
        raise BadRequestError(str(e)) from e
    return schemas.TaskRead.model_validate(task)


@router.post(
    "/tasks/picking-with-fefo",
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_permission("create", "tasks"))],
)
async def create_picking_task(
    body: PickingTaskCreate,
    session: SessionDep,
    user_id: UserDep,
) -> dict:
    service = TaskService(TaskRepository(session), TaskLineRepository(session), StockService(StockRepository(session)))
    try:
        result = await service.create_picking_with_fefo(
            user_id=user_id,
            document_id=body.document_id,
            assignee_id=body.assignee_id,
            warehouse_id=body.warehouse_id,
        )
    except ValueError as e:
        raise BadRequestError(str(e)) from e
    return result


@router.post("/tasks/{task_id}/lines", status_code=status.HTTP_201_CREATED, dependencies=[Depends(require_permission("update", "tasks"))])
async def add_task_line(
    task_id: int,
    body: schemas.TaskLineAdd,
    session: SessionDep,
    user_id: UserDep,
) -> dict:
    service = TaskService(TaskRepository(session), TaskLineRepository(session), StockService(StockRepository(session)))
    line = await service.add_line(user_id=user_id, task_id=task_id, **body.model_dump())
    return {"id": line.id}


@router.post("/tasks/{task_id}/start", response_model=schemas.TaskRead, dependencies=[Depends(require_permission("execute", "tasks"))])
async def start_task(
    task_id: int,
    session: SessionDep,
    user_id: UserDep,
) -> schemas.TaskRead:
    service = TaskService(TaskRepository(session), TaskLineRepository(session), StockService(StockRepository(session)))
    task = await service.start(user_id=user_id, task_id=task_id)
    if task is None:
        raise NotFoundError("Задание не найдено")
    return schemas.TaskRead.model_validate(task)


@router.get("/tasks/list", response_model=list[schemas.TaskList], dependencies=[Depends(require_permission("view", "tasks"))])
async def list_tasks_for_table(session: SessionDep) -> list[schemas.TaskList]:
    """Плоский список для таблицы."""
    from sqlalchemy.orm import selectinload
    from app.documents.models import Document
    from app.accounts.models import User
    from app.warehouse.models import Warehouse
    
    stmt = (
        select(Task)
        .options(
            selectinload(Task.document),
            selectinload(Task.assignee),
        )
    )
    rows = list(await session.scalars(stmt))

    result = []
    for r in rows:
        result.append(schemas.TaskList(
            id=r.id,
            is_active=r.is_active,
            is_deleted=r.is_deleted,
            created_at=r.created_at,
            updated_at=r.updated_at,
            created_by_id=r.created_by_id,
            updated_by_id=r.updated_by_id,
            deleted_at=r.deleted_at,
            deleted_by_id=r.deleted_by_id,
            task_type=r.task_type,
            status=r.status,
            status_label=TaskStatus(r.status).label if r.status in TaskStatus._value2member_map_ else r.status,
            assignee_id=r.assignee_id,
            document_number=r.document.document_number if r.document else None,
            assignee_name=r.assignee.username if r.assignee else None,
            warehouse_name=None,
        ))
    return result


@router.get("/tasks/{task_id}/detail", response_model=schemas.TaskDetail, dependencies=[Depends(require_permission("view", "tasks"))])
async def get_task_detail(task_id: int, session: SessionDep) -> schemas.TaskDetail:
    """Вложенная схема для детальной страницы."""
    task = await TaskRepository(session).get_by_id(task_id)
    if task is None:
        raise NotFoundError("Задание не найдено")
    return schemas.TaskDetail.model_validate(task)


@router.get("/tasks", response_model=list[schemas.TaskRead], dependencies=[Depends(require_permission("view", "tasks"))])
async def list_tasks(session: SessionDep,
) -> list[schemas.TaskRead]:
    repo = TaskRepository(session)
    rows = await repo.list_all()
    return [schemas.TaskRead.model_validate(r) for r in rows]


@router.patch("/tasks/{task_id}", response_model=schemas.TaskRead, dependencies=[Depends(require_permission("update", "tasks"))])
async def update_task(
    task_id: int,
    body: TaskUpdate,
    session: SessionDep,
    user_id: UserDep,
) -> schemas.TaskRead:
    """Обновить задание."""
    task = await TaskRepository(session).get_by_id(task_id)
    if task is None:
        raise NotFoundError("Задание не найдено")
    for field in ["task_type", "document_id", "assignee_id", "status"]:
        for field, value in body.model_dump(exclude_unset=True).items():
            setattr(task, field, value)
    task.updated_by_id = user_id
    try:
        await session.flush()
    except Exception as e:
        await session.rollback()
        raise HTTPException(status_code=500, detail=f"Ошибка базы данных: {e}")
    return schemas.TaskRead.model_validate(task)


@router.get("/tasks/{task_id}", response_model=schemas.TaskRead, dependencies=[Depends(require_permission("view", "tasks"))])
async def get_task(task_id: int, session: SessionDep) -> schemas.TaskRead:
    task = await TaskRepository(session).get_by_id(task_id)
    if task is None:
        raise NotFoundError("Задание не найдено")
    return schemas.TaskRead.model_validate(task)


@router.delete("/tasks/{task_id}", status_code=status.HTTP_204_NO_CONTENT, dependencies=[Depends(require_permission("delete", "tasks"))])
async def delete_task(task_id: int, session: SessionDep, user_id: UserDep) -> None:
    task = await TaskRepository(session).get_by_id(task_id)
    if task is None:
        raise NotFoundError("Задание не найдено")
    task.soft_delete(user_id)
    try:
        await session.flush()
    except Exception as e:
        await session.rollback()
        raise HTTPException(status_code=500, detail=f"Ошибка базы данных: {e}")


@router.post("/task-lines/{line_id}/complete", dependencies=[Depends(require_permission("execute", "tasks"))])
async def complete_task_line(
    line_id: int,
    body: schemas.TaskLineComplete,
    session: SessionDep,
    user_id: UserDep,
) -> dict:
    service = TaskService(TaskRepository(session), TaskLineRepository(session), StockService(StockRepository(session)))
    try:
        line = await service.complete_line(
            user_id=user_id,
            task_line_id=line_id,
            **body.model_dump(),
        )
    except ValueError as e:
        raise BadRequestError(str(e)) from e
    return {"id": line.id, "fact_qty": line.fact_qty}


@router.post("/tasks/{task_id}/complete", response_model=schemas.TaskRead, dependencies=[Depends(require_permission("complete", "tasks"))])
async def complete_task(
    task_id: int,
    body: schemas.TaskComplete,
    session: SessionDep,
    user_id: UserDep,
) -> schemas.TaskRead:
    service = TaskService(TaskRepository(session), TaskLineRepository(session), StockService(StockRepository(session)))
    try:
        task = await service.complete(user_id=user_id, task_id=task_id, force=body.force)
    except ValueError as e:
        raise BadRequestError(str(e)) from e
    return schemas.TaskRead.model_validate(task)
