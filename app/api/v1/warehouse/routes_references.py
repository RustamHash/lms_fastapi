"""API для справочников склада: группы, упаковки, связи товар-ячейка, движения."""

from __future__ import annotations

from fastapi import APIRouter, Depends, status
from sqlalchemy import select

from app.api.deps import SessionDep, UserDep, require_permission
from app.core.exceptions import ConflictError, NotFoundError
from app.warehouse.models import (
    ProductGroup,
    Package,
    ProductLocation,
    StockMovement,
)

router = APIRouter(prefix="/warehouse", tags=["warehouse-references"])


# ========== Группы товаров ==========

@router.get("/product-groups", dependencies=[Depends(require_permission("view", "products"))])
async def list_product_groups(session: SessionDep):
    rows = list(await session.scalars(select(ProductGroup)))
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
async def create_product_group(body: dict, session: SessionDep, user_id: UserDep):
    existing = await session.scalar(
        select(ProductGroup).where(ProductGroup.name == body["name"])
    )
    if existing:
        raise ConflictError(f"Группа {body['name']} уже существует")

    group = ProductGroup(
        name=body["name"],
        created_by_id=user_id,
        updated_by_id=user_id,
    )
    session.add(group)
    await session.flush()
    return {"id": group.id}


@router.get("/product-groups/{group_id}", dependencies=[Depends(require_permission("view", "products"))])
async def get_product_group(group_id: int, session: SessionDep):
    group = await session.get(ProductGroup, group_id)
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
async def update_product_group(group_id: int, body: dict, session: SessionDep, user_id: UserDep):
    group = await session.get(ProductGroup, group_id)
    if group is None:
        raise NotFoundError("Группа не найдена")
    group.name = body.get("name", group.name)
    group.updated_by_id = user_id
    await session.flush()
    return {"id": group.id}


@router.delete("/product-groups/{group_id}", status_code=status.HTTP_204_NO_CONTENT, dependencies=[Depends(require_permission("delete", "products"))])
async def delete_product_group(group_id: int, session: SessionDep, user_id: UserDep):
    group = await session.get(ProductGroup, group_id)
    if group is None:
        raise NotFoundError("Группа не найдена")
    group.soft_delete(user_id)
    await session.flush()


# ========== Упаковки ==========

@router.get("/packages", dependencies=[Depends(require_permission("view", "products"))])
async def list_packages(session: SessionDep, product_id: int | None = None):
    stmt = select(Package)
    if product_id:
        stmt = stmt.where(Package.product_id == product_id)
    rows = list(await session.scalars(stmt))
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
async def create_package(body: dict, session: SessionDep, user_id: UserDep):
    package = Package(
        product_id=body["product_id"],
        name=body["name"],
        quantity=body.get("quantity", 1),
        barcode=body.get("barcode"),
        weight=body.get("weight"),
        width=body.get("width"),
        height=body.get("height"),
        depth=body.get("depth"),
        is_base_unit=body.get("is_base_unit", False),
        created_by_id=user_id,
        updated_by_id=user_id,
    )
    session.add(package)
    await session.flush()
    return {"id": package.id}


@router.get("/packages/{package_id}", dependencies=[Depends(require_permission("view", "products"))])
async def get_package(package_id: int, session: SessionDep):
    p = await session.get(Package, package_id)
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
async def update_package(package_id: int, body: dict, session: SessionDep, user_id: UserDep):
    p = await session.get(Package, package_id)
    if p is None:
        raise NotFoundError("Упаковка не найдена")
    for field in ["name", "quantity", "barcode", "weight", "width", "height", "depth", "is_base_unit"]:
        if field in body:
            setattr(p, field, body[field])
    p.updated_by_id = user_id
    await session.flush()
    return {"id": p.id}


@router.delete("/packages/{package_id}", status_code=status.HTTP_204_NO_CONTENT, dependencies=[Depends(require_permission("delete", "products"))])
async def delete_package(package_id: int, session: SessionDep, user_id: UserDep):
    p = await session.get(Package, package_id)
    if p is None:
        raise NotFoundError("Упаковка не найдена")
    p.soft_delete(user_id)
    await session.flush()


# ========== Связи товар-ячейка ==========

@router.get("/product-locations", dependencies=[Depends(require_permission("view", "products"))])
async def list_product_locations(session: SessionDep):
    rows = list(await session.scalars(select(ProductLocation)))
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
async def create_product_location(body: dict, session: SessionDep, user_id: UserDep):
    pl = ProductLocation(
        product_id=body["product_id"],
        location_id=body["location_id"],
        created_by_id=user_id,
        updated_by_id=user_id,
    )
    session.add(pl)
    await session.flush()
    return {"id": pl.id}


@router.get("/product-locations/{pl_id}", dependencies=[Depends(require_permission("view", "products"))])
async def get_product_location(pl_id: int, session: SessionDep):
    pl = await session.get(ProductLocation, pl_id)
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
async def update_product_location(pl_id: int, body: dict, session: SessionDep, user_id: UserDep):
    pl = await session.get(ProductLocation, pl_id)
    if pl is None:
        raise NotFoundError("Связь не найдена")
    for field in ["product_id", "location_id"]:
        if field in body:
            setattr(pl, field, body[field])
    pl.updated_by_id = user_id
    await session.flush()
    return {"id": pl.id}


@router.delete("/product-locations/{pl_id}", status_code=status.HTTP_204_NO_CONTENT, dependencies=[Depends(require_permission("delete", "products"))])
async def delete_product_location(pl_id: int, session: SessionDep, user_id: UserDep):
    pl = await session.get(ProductLocation, pl_id)
    if pl is None:
        raise NotFoundError("Связь не найдена")
    pl.soft_delete(user_id)
    await session.flush()


# ========== Движения остатков ==========

@router.get("/stock-movements", dependencies=[Depends(require_permission("view", "stock"))])
async def list_stock_movements(session: SessionDep, product_id: int | None = None):
    stmt = select(StockMovement)
    if product_id:
        stmt = stmt.where(StockMovement.product_id == product_id)
    rows = list(await session.scalars(stmt))
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
async def create_stock_movement(body: dict, session: SessionDep, user_id: UserDep):
    sm = StockMovement(
        product_id=body["product_id"],
        document_id=body.get("document_id"),
        location_id=body["location_id"],
        lpn_id=body.get("lpn_id"),
        batch_id=body["batch_id"],
        direction=body["direction"],
        quantity=body["quantity"],
        created_by_id=user_id,
        updated_by_id=user_id,
    )
    session.add(sm)
    await session.flush()
    return {"id": sm.id}


@router.get("/stock-movements/{sm_id}", dependencies=[Depends(require_permission("view", "stock"))])
async def get_stock_movement(sm_id: int, session: SessionDep):
    sm = await session.get(StockMovement, sm_id)
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
async def update_stock_movement(sm_id: int, body: dict, session: SessionDep, user_id: UserDep):
    sm = await session.get(StockMovement, sm_id)
    if sm is None:
        raise NotFoundError("Движение не найдено")
    for field in ["quantity", "direction"]:
        if field in body:
            setattr(sm, field, body[field])
    sm.updated_by_id = user_id
    await session.flush()
    return {"id": sm.id}


@router.delete("/stock-movements/{sm_id}", status_code=status.HTTP_204_NO_CONTENT, dependencies=[Depends(require_permission("delete", "stock"))])
async def delete_stock_movement(sm_id: int, session: SessionDep, user_id: UserDep):
    sm = await session.get(StockMovement, sm_id)
    if sm is None:
        raise NotFoundError("Движение не найдено")
    sm.soft_delete(user_id)
    await session.flush()
