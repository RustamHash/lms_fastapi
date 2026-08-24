"""API для остатков."""

from __future__ import annotations

from fastapi import APIRouter, Depends, status

from app.api.deps import Services, UserDep, require_permission
from app.api.v1.warehouse.schemas import StockAdd, StockBalanceRead, StockMove, StockRemove
from app.core.exceptions import BadRequestError, NotFoundError

router = APIRouter(prefix="/warehouse", tags=["warehouse-stock"])


@router.get("/stock", response_model=list[StockBalanceRead], dependencies=[Depends(require_permission("view", "stock"))])
async def list_stock(services: Services) -> list[StockBalanceRead]:
    rows = await services.stock.list_all()
    return [StockBalanceRead.model_validate(r) for r in rows]


@router.get("/stock/{stock_id}", response_model=StockBalanceRead, dependencies=[Depends(require_permission("view", "stock"))])
async def get_stock(stock_id: int, services: Services) -> StockBalanceRead:
    stock = await services.stock.get_by_id(stock_id)
    if stock is None:
        raise NotFoundError("Остаток не найден")
    return StockBalanceRead.model_validate(stock)


@router.post("/stock/add", response_model=StockBalanceRead, dependencies=[Depends(require_permission("create", "stock"))])
async def add_stock(body: StockAdd, services: Services, user_id: UserDep) -> StockBalanceRead:
    try:
        balance = await services.stock.add_stock(user_id=user_id, **body.model_dump())
    except ValueError as e:
        raise BadRequestError(str(e)) from e
    return StockBalanceRead.model_validate(balance)


@router.post("/stock/remove", response_model=StockBalanceRead, dependencies=[Depends(require_permission("delete", "stock"))])
async def remove_stock(body: StockRemove, services: Services, user_id: UserDep) -> StockBalanceRead:
    try:
        balance = await services.stock.remove_stock(user_id=user_id, **body.model_dump())
    except ValueError as e:
        raise BadRequestError(str(e)) from e
    return StockBalanceRead.model_validate(balance)


@router.post("/stock/move", response_model=StockBalanceRead, dependencies=[Depends(require_permission("update", "stock"))])
async def move_stock(body: StockMove, services: Services, user_id: UserDep) -> StockBalanceRead:
    try:
        balance = await services.stock.move_stock(user_id=user_id, **body.model_dump())
    except ValueError as e:
        raise BadRequestError(str(e)) from e
    return StockBalanceRead.model_validate(balance)
