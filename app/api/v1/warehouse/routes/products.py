"""API для товаров, групп товаров, упаковок."""

from __future__ import annotations

from fastapi import APIRouter, Depends, status
from pydantic import BaseModel

from app.api.deps import Services, UserDep, require_permission
from app.api.v1.warehouse.schemas import ProductCreate, ProductRead
from app.core.exceptions import ConflictError, NotFoundError

router = APIRouter(prefix="/warehouse", tags=["warehouse-products"])


class ProductGroupCreate(BaseModel):
    name: str


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


class ProductLocationCreate(BaseModel):
    product_id: int
    location_id: int


# ========== Товары ==========

@router.get("/products", response_model=list[ProductRead], dependencies=[Depends(require_permission("view", "products"))])
async def list_products(services: Services, depositor_id: int | None = None) -> list[ProductRead]:
    if depositor_id:
        rows = await services.product.list_by_depositor(depositor_id)
    else:
        rows = await services.product.list_all()
    return [ProductRead.model_validate(r) for r in rows]


@router.post("/products", response_model=ProductRead, status_code=status.HTTP_201_CREATED, dependencies=[Depends(require_permission("create", "products"))])
async def create_product(body: ProductCreate, services: Services, user_id: UserDep) -> ProductRead:
    try:
        row = await services.product.create(user_id=user_id, **body.model_dump())
    except ValueError as e:
        raise ConflictError(str(e)) from e
    return ProductRead.model_validate(row)


@router.get("/products/{product_id}", response_model=ProductRead, dependencies=[Depends(require_permission("view", "products"))])
async def get_product(product_id: int, services: Services) -> ProductRead:
    product = await services.product.get_by_id(product_id)
    if product is None:
        raise NotFoundError("Товар не найден")
    return ProductRead.model_validate(product)


@router.patch("/products/{product_id}", response_model=ProductRead, dependencies=[Depends(require_permission("update", "products"))])
async def update_product(product_id: int, body: ProductCreate, services: Services, user_id: UserDep) -> ProductRead:
    product = await services.product.update(product_id, user_id=user_id, **body.model_dump(exclude_unset=True))
    if product is None:
        raise NotFoundError("Товар не найден")
    return ProductRead.model_validate(product)


@router.delete("/products/{product_id}", status_code=status.HTTP_204_NO_CONTENT, dependencies=[Depends(require_permission("delete", "products"))])
async def delete_product(product_id: int, services: Services, user_id: UserDep) -> None:
    ok = await services.product.soft_delete(product_id, user_id)
    if not ok:
        raise NotFoundError("Товар не найден")


# ========== Группы товаров ==========

@router.get("/product-groups", dependencies=[Depends(require_permission("view", "products"))])
async def list_product_groups(services: Services):
    from app.warehouse.repository import ProductGroupRepository
    rows = await ProductGroupRepository(services.product._repo._s).list_all()
    return [{"id": g.id, "name": g.name} for g in rows]


@router.post("/product-groups", status_code=status.HTTP_201_CREATED, dependencies=[Depends(require_permission("create", "products"))])
async def create_product_group(body: ProductGroupCreate, services: Services, user_id: UserDep):
    from app.warehouse.repository import ProductGroupRepository
    repo = ProductGroupRepository(services.product._repo._s)
    existing = await repo.get_by_name(body.name)
    if existing:
        raise ConflictError(f"Группа {body.name} уже существует")
    group = await repo.create(name=body.name)
    return {"id": group.id}


@router.get("/product-groups/{group_id}", dependencies=[Depends(require_permission("view", "products"))])
async def get_product_group(group_id: int, services: Services):
    from app.warehouse.repository import ProductGroupRepository
    group = await ProductGroupRepository(services.product._repo._s).get_by_id(group_id)
    if group is None:
        raise NotFoundError("Группа не найдена")
    return {"id": group.id, "name": group.name}


@router.patch("/product-groups/{group_id}", dependencies=[Depends(require_permission("update", "products"))])
async def update_product_group(group_id: int, body: ProductGroupCreate, services: Services, user_id: UserDep):
    from app.warehouse.repository import ProductGroupRepository
    group = await ProductGroupRepository(services.product._repo._s).update(group_id, name=body.name)
    if group is None:
        raise NotFoundError("Группа не найдена")
    return {"id": group.id}


@router.delete("/product-groups/{group_id}", status_code=status.HTTP_204_NO_CONTENT, dependencies=[Depends(require_permission("delete", "products"))])
async def delete_product_group(group_id: int, services: Services, user_id: UserDep):
    from app.warehouse.repository import ProductGroupRepository
    ok = await ProductGroupRepository(services.product._repo._s).soft_delete(group_id, user_id)
    if not ok:
        raise NotFoundError("Группа не найдена")


# ========== Упаковки ==========

@router.get("/packages", dependencies=[Depends(require_permission("view", "products"))])
async def list_packages(services: Services):
    from app.warehouse.repository import PackageRepository
    rows = await PackageRepository(services.product._repo._s).list_all()
    return [{"id": p.id, "product_id": p.product_id, "name": p.name, "barcode": p.barcode, "weight": p.weight} for p in rows]


@router.post("/packages", status_code=status.HTTP_201_CREATED, dependencies=[Depends(require_permission("create", "products"))])
async def create_package(body: PackageCreate, services: Services, user_id: UserDep):
    from app.warehouse.repository import PackageRepository
    package = await PackageRepository(services.product._repo._s).create(**body.model_dump())
    return {"id": package.id}


@router.get("/packages/{package_id}", dependencies=[Depends(require_permission("view", "products"))])
async def get_package(package_id: int, services: Services):
    from app.warehouse.repository import PackageRepository
    package = await PackageRepository(services.product._repo._s).get_by_id(package_id)
    if package is None:
        raise NotFoundError("Упаковка не найдена")
    return {"id": package.id, "product_id": package.product_id, "name": package.name}


@router.patch("/packages/{package_id}", dependencies=[Depends(require_permission("update", "products"))])
async def update_package(package_id: int, body: PackageCreate, services: Services, user_id: UserDep):
    from app.warehouse.repository import PackageRepository
    package = await PackageRepository(services.product._repo._s).update(package_id, **body.model_dump(exclude_unset=True))
    if package is None:
        raise NotFoundError("Упаковка не найдена")
    return {"id": package.id}


@router.delete("/packages/{package_id}", status_code=status.HTTP_204_NO_CONTENT, dependencies=[Depends(require_permission("delete", "products"))])
async def delete_package(package_id: int, services: Services, user_id: UserDep):
    from app.warehouse.repository import PackageRepository
    ok = await PackageRepository(services.product._repo._s).soft_delete(package_id, user_id)
    if not ok:
        raise NotFoundError("Упаковка не найдена")


# ========== Связи товар-ячейка ==========

@router.get("/product-locations", dependencies=[Depends(require_permission("view", "products"))])
async def list_product_locations(services: Services):
    from app.warehouse.repository import ProductLocationRepository
    rows = await ProductLocationRepository(services.product._repo._s).list_all()
    return [{"id": pl.id, "product_id": pl.product_id, "location_id": pl.location_id} for pl in rows]


@router.post("/product-locations", status_code=status.HTTP_201_CREATED, dependencies=[Depends(require_permission("create", "products"))])
async def create_product_location(body: ProductLocationCreate, services: Services, user_id: UserDep):
    from app.warehouse.repository import ProductLocationRepository
    pl = await ProductLocationRepository(services.product._repo._s).create(**body.model_dump())
    return {"id": pl.id}


@router.delete("/product-locations/{pl_id}", status_code=status.HTTP_204_NO_CONTENT, dependencies=[Depends(require_permission("delete", "products"))])
async def delete_product_location(pl_id: int, services: Services, user_id: UserDep):
    from app.warehouse.repository import ProductLocationRepository
    ok = await ProductLocationRepository(services.product._repo._s).soft_delete(pl_id, user_id)
    if not ok:
        raise NotFoundError("Связь не найдена")
