"""API для остатков."""

from __future__ import annotations

from fastapi import APIRouter, Depends

from app.api.deps import UserDep, require_permission
from app.api.v1.warehouse.deps import get_stock_service
from app.api.v1.warehouse.schemas import StockAdd, StockBalanceRead, StockMove, StockRemove
from app.core.exceptions import NotFoundError
from app.warehouse.services.stock_service import StockService

router = APIRouter(prefix="/warehouse", tags=["warehouse-stock"])


@router.get("/stock", response_model=list[StockBalanceRead], dependencies=[Depends(require_permission("view", "stock"))])
async def list_stock(service: StockService = Depends(get_stock_service)) -> list[StockBalanceRead]:
    rows = await service.list_all()
    return [StockBalanceRead.model_validate(r) for r in rows]


@router.get("/stock/{stock_id}", response_model=StockBalanceRead, dependencies=[Depends(require_permission("view", "stock"))])
async def get_stock(
    stock_id: int,
    service: StockService = Depends(get_stock_service),
) -> StockBalanceRead:
    stock = await service.get_by_id(stock_id)
    if stock is None:
        raise NotFoundError("Остаток не найден")
    return StockBalanceRead.model_validate(stock)


@router.post("/stock/add", response_model=StockBalanceRead, dependencies=[Depends(require_permission("create", "stock"))])
async def add_stock(
    body: StockAdd,
    user_id: UserDep,
    service: StockService = Depends(get_stock_service),
) -> StockBalanceRead:
    balance = await service.add_stock(user_id=user_id, **body.model_dump())
    return StockBalanceRead.model_validate(balance)


@router.post("/stock/remove", response_model=StockBalanceRead, dependencies=[Depends(require_permission("delete", "stock"))])
async def remove_stock(
    body: StockRemove,
    user_id: UserDep,
    service: StockService = Depends(get_stock_service),
) -> StockBalanceRead:
    balance = await service.remove_stock(user_id=user_id, **body.model_dump())
    return StockBalanceRead.model_validate(balance)


@router.post("/stock/move", response_model=StockBalanceRead, dependencies=[Depends(require_permission("update", "stock"))])
async def move_stock(
    body: StockMove,
    user_id: UserDep,
    service: StockService = Depends(get_stock_service),
) -> StockBalanceRead:
    balance = await service.move_stock(user_id=user_id, **body.model_dump())
    return StockBalanceRead.model_validate(balance)
