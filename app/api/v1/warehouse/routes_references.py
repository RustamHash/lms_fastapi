"""API для справочников склада: группы, упаковки, связи товар-ячейка, движения."""

from __future__ import annotations

from pydantic import BaseModel
from fastapi import HTTPException, APIRouter, Depends, status
from sqlalchemy import select

from app.api.deps import SessionDep, UserDep, require_permission
from app.core.exceptions import ConflictError, NotFoundError
from app.warehouse.models import (
    ProductGroup,
    Package,
    ProductLocation,
    StockMovement,
)
from app.warehouse.repository import (
    PackageRepository,
    ProductGroupRepository,
    ProductLocationRepository,
    StockRepository,
)

router = APIRouter(prefix="/warehouse", tags=["warehouse-references"])


class ProductGroupCreate(BaseModel):
    name: str


class ProductGroupUpdate(BaseModel):
    name: str | None = None


class PackageCreate(BaseModel):
    product_id: int
    name: str
    quantity: int = 1
    barcode: str | None = None
    weight: float | None = None
    width: float | None = None
    height: float | None = None
    depth: float | None = None
    is_base_unit: bool = False


class PackageUpdate(BaseModel):
    name: str | None = None
    quantity: int | None = None
    barcode: str | None = None
    weight: float | None = None
    width: float | None = None
    height: float | None = None
    depth: float | None = None
    is_base_unit: bool | None = None


class ProductLocationCreate(BaseModel):
    product_id: int
    location_id: int


class ProductLocationUpdate(BaseModel):
    product_id: int | None = None
    location_id: int | None = None


class StockMovementCreate(BaseModel):
    product_id: int
    location_id: int
    direction: str
    quantity: float
    document_id: int | None = None
    lpn_id: int | None = None
    batch_id: int | None = None


class StockMovementUpdate(BaseModel):
    quantity: float | None = None
    direction: str | None = None


# ========== Группы товаров ==========

@router.get("/product-groups", dependencies=[Depends(require_permission("view", "products"))])
async def list_product_groups(session: SessionDep):
    rows = await ProductGroupRepository(session).list_all()
    return [
        {
            "id": g.id,
            "name": g.name,
            "is_active": g.is_active,
            "is_deleted": g.is_deleted,
            "created_at": g.created_at,
            "updated_at": g.updated_at,
        }
        for g in rows
    ]


@router.post("/product-groups", status_code=status.HTTP_201_CREATED, dependencies=[Depends(require_permission("create", "products"))])
async def create_product_group(body: ProductGroupCreate, session: SessionDep, user_id: UserDep):
    existing = await ProductGroupRepository(session).get_by_name(body.name)
    if existing:
        raise ConflictError(f"Группа {body['name']} уже существует")

    group = ProductGroup(
        name=body.name,
    )
    session.add(group)
    try:
        await session.flush()
    except Exception as e:
        await session.rollback()
        raise HTTPException(status_code=500, detail=f"Ошибка базы данных: {e}")
    return {"id": group.id}


@router.get("/product-groups/{group_id}", dependencies=[Depends(require_permission("view", "products"))])
async def get_product_group(group_id: int, session: SessionDep):
    group = await ProductGroupRepository(session).get_by_id(group_id)
    if group is None:
        raise NotFoundError("Группа не найдена")
    return {
        "id": group.id,
        "name": group.name,
        "is_active": group.is_active,
        "is_deleted": group.is_deleted,
        "created_at": group.created_at,
        "updated_at": group.updated_at,
    }


@router.patch("/product-groups/{group_id}", dependencies=[Depends(require_permission("update", "products"))])
async def update_product_group(group_id: int, body: ProductGroupUpdate, session: SessionDep, user_id: UserDep):
    group = await ProductGroupRepository(session).get_by_id(group_id)
    if group is None:
        raise NotFoundError("Группа не найдена")
    group.name = body.name if body.name else group.name
    group.updated_by_id = user_id
    try:
        await session.flush()
    except Exception as e:
        await session.rollback()
        raise HTTPException(status_code=500, detail=f"Ошибка базы данных: {e}")
    return {"id": group.id}


@router.delete("/product-groups/{group_id}", status_code=status.HTTP_204_NO_CONTENT, dependencies=[Depends(require_permission("delete", "products"))])
async def delete_product_group(group_id: int, session: SessionDep, user_id: UserDep):
    group = await ProductGroupRepository(session).get_by_id(group_id)
    if group is None:
        raise NotFoundError("Группа не найдена")
    group.soft_delete(user_id)
    try:
        await session.flush()
    except Exception as e:
        await session.rollback()
        raise HTTPException(status_code=500, detail=f"Ошибка базы данных: {e}")


# ========== Упаковки ==========

@router.get("/packages", dependencies=[Depends(require_permission("view", "products"))])
async def list_packages(session: SessionDep, product_id: int | None = None):
    rows = await PackageRepository(session).list_all()
    return [
        {
            "id": p.id,
            "product_id": p.product_id,
            "name": p.name,
            "quantity": p.quantity,
            "barcode": p.barcode,
            "weight": p.weight,
            "width": p.width,
            "height": p.height,
            "depth": p.depth,
            "is_base_unit": p.is_base_unit,
            "is_active": p.is_active,
            "is_deleted": p.is_deleted,
            "created_at": p.created_at,
            "updated_at": p.updated_at,
        }
        for p in rows
    ]


@router.post("/packages", status_code=status.HTTP_201_CREATED, dependencies=[Depends(require_permission("create", "products"))])
async def create_package(body: PackageCreate, session: SessionDep, user_id: UserDep):
    package = Package(
        product_id=body.product_id,
        name=body.name,
        quantity=body.quantity,
        barcode=body.barcode,
        weight=body.weight,
        width=body.width,
        height=body.height,
        depth=body.depth,
        is_base_unit=body.is_base_unit,
    )
    session.add(package)
    try:
        await session.flush()
    except Exception as e:
        await session.rollback()
        raise HTTPException(status_code=500, detail=f"Ошибка базы данных: {e}")
    return {"id": package.id}


@router.get("/packages/{package_id}", dependencies=[Depends(require_permission("view", "products"))])
async def get_package(package_id: int, session: SessionDep):
    p = await PackageRepository(session).get_by_id(package_id)
    if p is None:
        raise NotFoundError("Упаковка не найдена")
    return {
        "id": p.id,
        "product_id": p.product_id,
        "name": p.name,
        "quantity": p.quantity,
        "barcode": p.barcode,
        "weight": p.weight,
        "width": p.width,
        "height": p.height,
        "depth": p.depth,
        "is_base_unit": p.is_base_unit,
        "is_active": p.is_active,
        "is_deleted": p.is_deleted,
        "created_at": p.created_at,
        "updated_at": p.updated_at,
    }


@router.patch("/packages/{package_id}", dependencies=[Depends(require_permission("update", "products"))])
async def update_package(package_id: int, body: PackageUpdate, session: SessionDep, user_id: UserDep):
    p = await PackageRepository(session).get_by_id(package_id)
    if p is None:
        raise NotFoundError("Упаковка не найдена")
    for field in ["name", "quantity", "barcode", "weight", "width", "height", "depth", "is_base_unit"]:
        for field, value in body.model_dump(exclude_unset=True).items():
            setattr(p, field, value)
    p.updated_by_id = user_id
    try:
        await session.flush()
    except Exception as e:
        await session.rollback()
        raise HTTPException(status_code=500, detail=f"Ошибка базы данных: {e}")
    return {"id": p.id}


@router.delete("/packages/{package_id}", status_code=status.HTTP_204_NO_CONTENT, dependencies=[Depends(require_permission("delete", "products"))])
async def delete_package(package_id: int, session: SessionDep, user_id: UserDep):
    p = await PackageRepository(session).get_by_id(package_id)
    if p is None:
        raise NotFoundError("Упаковка не найдена")
    p.soft_delete(user_id)
    try:
        await session.flush()
    except Exception as e:
        await session.rollback()
        raise HTTPException(status_code=500, detail=f"Ошибка базы данных: {e}")


# ========== Связи товар-ячейка ==========

@router.get("/product-locations", dependencies=[Depends(require_permission("view", "products"))])
async def list_product_locations(session: SessionDep):
    rows = await ProductLocationRepository(session).list_all()
    return [
        {
            "id": pl.id,
            "product_id": pl.product_id,
            "location_id": pl.location_id,
            "is_active": pl.is_active,
            "is_deleted": pl.is_deleted,
            "created_at": pl.created_at,
            "updated_at": pl.updated_at,
        }
        for pl in rows
    ]


@router.post("/product-locations", status_code=status.HTTP_201_CREATED, dependencies=[Depends(require_permission("create", "products"))])
async def create_product_location(body: ProductLocationCreate, session: SessionDep, user_id: UserDep):
    pl = ProductLocation(
        product_id=body.product_id,
        location_id=body.location_id,
    )
    session.add(pl)
    try:
        await session.flush()
    except Exception as e:
        await session.rollback()
        raise HTTPException(status_code=500, detail=f"Ошибка базы данных: {e}")
    return {"id": pl.id}


@router.get("/product-locations/{pl_id}", dependencies=[Depends(require_permission("view", "products"))])
async def get_product_location(pl_id: int, session: SessionDep):
    pl = await ProductLocationRepository(session).get_by_id(pl_id)
    if pl is None:
        raise NotFoundError("Связь не найдена")
    return {
        "id": pl.id,
        "product_id": pl.product_id,
        "location_id": pl.location_id,
        "is_active": pl.is_active,
        "is_deleted": pl.is_deleted,
        "created_at": pl.created_at,
        "updated_at": pl.updated_at,
    }


@router.patch("/product-locations/{pl_id}", dependencies=[Depends(require_permission("update", "products"))])
async def update_product_location(pl_id: int, body: ProductLocationUpdate, session: SessionDep, user_id: UserDep):
    pl = await ProductLocationRepository(session).get_by_id(pl_id)
    if pl is None:
        raise NotFoundError("Связь не найдена")
    for field in ["product_id", "location_id"]:
        if field in body:
            setattr(pl, field, body[field])
    pl.updated_by_id = user_id
    try:
        await session.flush()
    except Exception as e:
        await session.rollback()
        raise HTTPException(status_code=500, detail=f"Ошибка базы данных: {e}")
    return {"id": pl.id}


@router.delete("/product-locations/{pl_id}", status_code=status.HTTP_204_NO_CONTENT, dependencies=[Depends(require_permission("delete", "products"))])
async def delete_product_location(pl_id: int, session: SessionDep, user_id: UserDep):
    pl = await ProductLocationRepository(session).get_by_id(pl_id)
    if pl is None:
        raise NotFoundError("Связь не найдена")
    pl.soft_delete(user_id)
    try:
        await session.flush()
    except Exception as e:
        await session.rollback()
        raise HTTPException(status_code=500, detail=f"Ошибка базы данных: {e}")


# ========== Движения остатков ==========

@router.get("/stock-movements", dependencies=[Depends(require_permission("view", "stock"))])
async def list_stock_movements(session: SessionDep, product_id: int | None = None):
    rows = await StockRepository(session).list_movements()
    return [
        {
            "id": sm.id,
            "product_id": sm.product_id,
            "document_id": sm.document_id,
            "location_id": sm.location_id,
            "lpn_id": sm.lpn_id,
            "batch_id": sm.batch_id,
            "direction": sm.direction,
            "quantity": sm.quantity,
            "is_active": sm.is_active,
            "is_deleted": sm.is_deleted,
            "created_at": sm.created_at,
            "updated_at": sm.updated_at,
        }
        for sm in rows
    ]


@router.post("/stock-movements", status_code=status.HTTP_201_CREATED, dependencies=[Depends(require_permission("create", "stock"))])
async def create_stock_movement(body: StockMovementCreate, session: SessionDep, user_id: UserDep):
    sm = StockMovement(
        product_id=body.product_id,
        document_id=body.document_id,
        location_id=body.location_id,
        lpn_id=body.lpn_id,
        batch_id=body["batch_id"],
        direction=body.direction,
        quantity=body.quantity,
    )
    session.add(sm)
    try:
        await session.flush()
    except Exception as e:
        await session.rollback()
        raise HTTPException(status_code=500, detail=f"Ошибка базы данных: {e}")
    return {"id": sm.id}


@router.get("/stock-movements/{sm_id}", dependencies=[Depends(require_permission("view", "stock"))])
async def get_stock_movement(sm_id: int, session: SessionDep):
    sm = await StockRepository(session).get_movement_by_id(sm_id)
    if sm is None:
        raise NotFoundError("Движение не найдено")
    return {
        "id": sm.id,
        "product_id": sm.product_id,
        "document_id": sm.document_id,
        "location_id": sm.location_id,
        "lpn_id": sm.lpn_id,
        "batch_id": sm.batch_id,
        "direction": sm.direction,
        "quantity": sm.quantity,
        "is_active": sm.is_active,
        "is_deleted": sm.is_deleted,
        "created_at": sm.created_at,
        "updated_at": sm.updated_at,
    }


@router.patch("/stock-movements/{sm_id}", dependencies=[Depends(require_permission("update", "stock"))])
async def update_stock_movement(sm_id: int, body: StockMovementUpdate, session: SessionDep, user_id: UserDep):
    sm = await StockRepository(session).get_movement_by_id(sm_id)
    if sm is None:
        raise NotFoundError("Движение не найдено")
    for field in ["quantity", "direction"]:
        if field in body:
            setattr(sm, field, body[field])
    sm.updated_by_id = user_id
    try:
        await session.flush()
    except Exception as e:
        await session.rollback()
        raise HTTPException(status_code=500, detail=f"Ошибка базы данных: {e}")
    return {"id": sm.id}


@router.delete("/stock-movements/{sm_id}", status_code=status.HTTP_204_NO_CONTENT, dependencies=[Depends(require_permission("delete", "stock"))])
async def delete_stock_movement(sm_id: int, session: SessionDep, user_id: UserDep):
    sm = await StockRepository(session).get_movement_by_id(sm_id)
    if sm is None:
        raise NotFoundError("Движение не найдено")
    sm.soft_delete(user_id)
    try:
        await session.flush()
    except Exception as e:
        await session.rollback()
        raise HTTPException(status_code=500, detail=f"Ошибка базы данных: {e}")
