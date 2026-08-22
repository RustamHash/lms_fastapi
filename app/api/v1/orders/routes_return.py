"""API для возвратов."""

from __future__ import annotations

from fastapi import HTTPException, APIRouter, Depends, status

from app.api.deps import SessionDep, UserDep, require_permission
from app.api.v1.orders.schemas import (
    ReturnOrderCreate,
    ReturnOrderLineCreate,
    ReturnOrderLineRead,
    ReturnOrderRead,
    ReturnOrderUpdate,
)
from app.core.exceptions import NotFoundError
from app.orders.repository import ReturnOrderLineRepository, ReturnOrderRepository

router = APIRouter(prefix="/return-orders", tags=["return-orders"])


@router.get("", response_model=list[ReturnOrderRead], dependencies=[Depends(require_permission("view", "orders"))])
async def list_return_orders(session: SessionDep,
) -> list[ReturnOrderRead]:
    repo = ReturnOrderRepository(session)
    rows = await repo.list_all()
    return [ReturnOrderRead.model_validate(r) for r in rows]


@router.post("", response_model=ReturnOrderRead, status_code=status.HTTP_201_CREATED, dependencies=[Depends(require_permission("create", "orders"))])
async def create_return_order(body: ReturnOrderCreate, session: SessionDep, user_id: UserDep) -> ReturnOrderRead:
    order = ReturnOrder(created_by_id=user_id, **body.model_dump())
    session.add(order)
    try:
        await session.flush()
    except Exception as e:
        await session.rollback()
        raise HTTPException(status_code=500, detail=f"Ошибка базы данных: {e}")
    return ReturnOrderRead.model_validate(order)


@router.get("/{order_id}", response_model=ReturnOrderRead, dependencies=[Depends(require_permission("view", "orders"))])
async def get_return_order(order_id: int, session: SessionDep) -> ReturnOrderRead:
    order = await ReturnOrderRepository(session).get_by_id(order_id)
    if order is None:
        raise NotFoundError("Возврат не найден")
    return ReturnOrderRead.model_validate(order)


@router.patch("/{order_id}", response_model=ReturnOrderRead, dependencies=[Depends(require_permission("update", "orders"))])
async def update_return_order(order_id: int, body: ReturnOrderUpdate, session: SessionDep, user_id: UserDep) -> ReturnOrderRead:
    order = await ReturnOrderRepository(session).get_by_id(order_id)
    if order is None:
        raise NotFoundError("Возврат не найден")
    for field, value in body.model_dump(exclude_unset=True).items():
        setattr(order, field, value)
    order.updated_by_id = user_id
    try:
        await session.flush()
    except Exception as e:
        await session.rollback()
        raise HTTPException(status_code=500, detail=f"Ошибка базы данных: {e}")
    return ReturnOrderRead.model_validate(order)


@router.delete("/{order_id}", status_code=status.HTTP_204_NO_CONTENT, dependencies=[Depends(require_permission("delete", "orders"))])
async def delete_return_order(order_id: int, session: SessionDep, user_id: UserDep) -> None:
    order = await ReturnOrderRepository(session).get_by_id(order_id)
    if order is None:
        raise NotFoundError("Возврат не найден")
    order.soft_delete(user_id)
    try:
        await session.flush()
    except Exception as e:
        await session.rollback()
        raise HTTPException(status_code=500, detail=f"Ошибка базы данных: {e}")


# ========== Строки ==========

@router.get("/{order_id}/lines", response_model=list[ReturnOrderLineRead], dependencies=[Depends(require_permission("view", "orders"))])
async def list_return_lines(order_id: int, session: SessionDep) -> list[ReturnOrderLineRead]:
    rows = await ReturnOrderLineRepository(session).list_by_order(order_id)
    return [ReturnOrderLineRead.model_validate(r) for r in rows]


@router.get("/lines/{line_id}", response_model=ReturnOrderLineRead, dependencies=[Depends(require_permission("view", "orders"))])
async def get_return_line(line_id: int, session: SessionDep) -> ReturnOrderLineRead:
    line = await ReturnOrderLineRepository(session).get_by_id(line_id)
    if line is None:
        raise NotFoundError("Строка не найдена")
    return ReturnOrderLineRead.model_validate(line)


@router.patch("/lines/{line_id}", response_model=ReturnOrderLineRead, dependencies=[Depends(require_permission("update", "orders"))])
async def update_return_line(line_id: int, body: ReturnOrderLineCreate, session: SessionDep, user_id: UserDep) -> ReturnOrderLineRead:
    line = await ReturnOrderLineRepository(session).get_by_id(line_id)
    if line is None:
        raise NotFoundError("Строка не найдена")
    for field, value in body.model_dump(exclude_unset=True, exclude={"return_order_id"}).items():
        setattr(line, field, value)
    line.updated_by_id = user_id
    try:
        await session.flush()
    except Exception as e:
        await session.rollback()
        raise HTTPException(status_code=500, detail=f"Ошибка базы данных: {e}")
    return ReturnOrderLineRead.model_validate(line)


@router.delete("/lines/{line_id}", status_code=status.HTTP_204_NO_CONTENT, dependencies=[Depends(require_permission("delete", "orders"))])
async def delete_return_line(line_id: int, session: SessionDep, user_id: UserDep) -> None:
    line = await ReturnOrderLineRepository(session).get_by_id(line_id)
    if line is None:
        raise NotFoundError("Строка не найдена")
    line.soft_delete(user_id)
    try:
        await session.flush()
    except Exception as e:
        await session.rollback()
        raise HTTPException(status_code=500, detail=f"Ошибка базы данных: {e}")


@router.post("/{order_id}/lines", response_model=ReturnOrderLineRead, status_code=status.HTTP_201_CREATED, dependencies=[Depends(require_permission("create", "orders"))])
async def create_return_line(order_id: int, body: ReturnOrderLineCreate, session: SessionDep, user_id: UserDep) -> ReturnOrderLineRead:
    line = ReturnOrderLine(return_order_id=order_id, **body.model_dump(exclude={"return_order_id"}))
    session.add(line)
    try:
        await session.flush()
    except Exception as e:
        await session.rollback()
        raise HTTPException(status_code=500, detail=f"Ошибка базы данных: {e}")
    return ReturnOrderLineRead.model_validate(line)
