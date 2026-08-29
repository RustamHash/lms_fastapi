"""API для товаров, групп товаров, упаковок."""

from __future__ import annotations

from fastapi import APIRouter, Depends, status

from app.api.deps import ScopeDep, UserDep, require_permission
from app.api.v1.warehouse.deps import (
    get_package_service,
    get_product_group_service,
    get_product_location_service,
    get_product_service,
)
from app.api.v1.warehouse.schemas import (
    PackageCreate,
    ProductCreate,
    ProductGroupCreate,
    ProductLocationCreate,
    ProductRead,
)
from app.core.exceptions import ConflictError, ForbiddenError, NotFoundError
from app.warehouse.services.package_service import PackageService
from app.warehouse.services.product_group_service import ProductGroupService
from app.warehouse.services.product_location_service import ProductLocationService
from app.warehouse.services.product_service import ProductService

router = APIRouter(prefix="/warehouse", tags=["warehouse-products"])


@router.get("/products", response_model=list[ProductRead], dependencies=[Depends(require_permission("view", "products"))])
async def list_products(
    scope: ScopeDep,
    service: ProductService = Depends(get_product_service),
    depositor_id: int | None = None,
) -> list[ProductRead]:
    if depositor_id is not None:
        if not scope.allows_depositor(depositor_id):
            raise ForbiddenError("Нет доступа к поклажедателю")
        rows = await service.list_by_depositor(depositor_id, scope=scope)
    else:
        rows = await service.list_all(scope=scope)
    return [ProductRead.model_validate(r) for r in rows]


@router.post("/products", response_model=ProductRead, status_code=status.HTTP_201_CREATED, dependencies=[Depends(require_permission("create", "products"))])
async def create_product(
    body: ProductCreate,
    user_id: UserDep,
    scope: ScopeDep,
    service: ProductService = Depends(get_product_service),
) -> ProductRead:
    if not scope.allows_depositor(body.depositor_id):
        raise ForbiddenError("Нет доступа к поклажедателю")
    try:
        row = await service.create(user_id=user_id, **body.model_dump())
    except ValueError as e:
        raise ConflictError(str(e)) from e
    return ProductRead.model_validate(row)


@router.get("/products/{product_id}", response_model=ProductRead, dependencies=[Depends(require_permission("view", "products"))])
async def get_product(
    product_id: int,
    scope: ScopeDep,
    service: ProductService = Depends(get_product_service),
) -> ProductRead:
    product = await service.get_by_id(product_id, scope=scope)
    if product is None:
        raise NotFoundError("Товар не найден")
    return ProductRead.model_validate(product)


@router.patch("/products/{product_id}", response_model=ProductRead, dependencies=[Depends(require_permission("update", "products"))])
async def update_product(
    product_id: int,
    body: ProductCreate,
    user_id: UserDep,
    service: ProductService = Depends(get_product_service),
) -> ProductRead:
    product = await service.update(product_id, user_id=user_id, **body.model_dump(exclude_unset=True))
    if product is None:
        raise NotFoundError("Товар не найден")
    return ProductRead.model_validate(product)


@router.delete("/products/{product_id}", status_code=status.HTTP_204_NO_CONTENT, dependencies=[Depends(require_permission("delete", "products"))])
async def delete_product(
    product_id: int,
    user_id: UserDep,
    service: ProductService = Depends(get_product_service),
) -> None:
    ok = await service.soft_delete(product_id, user_id)
    if not ok:
        raise NotFoundError("Товар не найден")


@router.get("/product-groups", dependencies=[Depends(require_permission("view", "products"))])
async def list_product_groups(
    service: ProductGroupService = Depends(get_product_group_service),
):
    rows = await service.list_all()
    return [{"id": g.id, "name": g.name} for g in rows]


@router.post("/product-groups", status_code=status.HTTP_201_CREATED, dependencies=[Depends(require_permission("create", "products"))])
async def create_product_group(
    body: ProductGroupCreate,
    service: ProductGroupService = Depends(get_product_group_service),
):
    group = await service.create(name=body.name)
    return {"id": group.id}


@router.get("/product-groups/{group_id}", dependencies=[Depends(require_permission("view", "products"))])
async def get_product_group(
    group_id: int,
    service: ProductGroupService = Depends(get_product_group_service),
):
    group = await service.get_by_id(group_id)
    if group is None:
        raise NotFoundError("Группа не найдена")
    return {"id": group.id, "name": group.name}


@router.patch("/product-groups/{group_id}", dependencies=[Depends(require_permission("update", "products"))])
async def update_product_group(
    group_id: int,
    body: ProductGroupCreate,
    service: ProductGroupService = Depends(get_product_group_service),
):
    group = await service.update(group_id, name=body.name)
    if group is None:
        raise NotFoundError("Группа не найдена")
    return {"id": group.id}


@router.delete("/product-groups/{group_id}", status_code=status.HTTP_204_NO_CONTENT, dependencies=[Depends(require_permission("delete", "products"))])
async def delete_product_group(
    group_id: int,
    user_id: UserDep,
    service: ProductGroupService = Depends(get_product_group_service),
) -> None:
    ok = await service.soft_delete(group_id, user_id)
    if not ok:
        raise NotFoundError("Группа не найдена")


@router.get("/packages", dependencies=[Depends(require_permission("view", "products"))])
async def list_packages(service: PackageService = Depends(get_package_service)):
    rows = await service.list_all()
    return [
        {
            "id": p.id,
            "product_id": p.product_id,
            "name": p.name,
            "barcode": p.barcode,
            "weight": p.weight,
        }
        for p in rows
    ]


@router.post("/packages", status_code=status.HTTP_201_CREATED, dependencies=[Depends(require_permission("create", "products"))])
async def create_package(
    body: PackageCreate,
    service: PackageService = Depends(get_package_service),
):
    package = await service.create(**body.model_dump())
    return {"id": package.id}


@router.get("/packages/{package_id}", dependencies=[Depends(require_permission("view", "products"))])
async def get_package(
    package_id: int,
    service: PackageService = Depends(get_package_service),
):
    package = await service.get_by_id(package_id)
    if package is None:
        raise NotFoundError("Упаковка не найдена")
    return {"id": package.id, "product_id": package.product_id, "name": package.name}


@router.patch("/packages/{package_id}", dependencies=[Depends(require_permission("update", "products"))])
async def update_package(
    package_id: int,
    body: PackageCreate,
    service: PackageService = Depends(get_package_service),
):
    package = await service.update(package_id, **body.model_dump(exclude_unset=True))
    if package is None:
        raise NotFoundError("Упаковка не найдена")
    return {"id": package.id}


@router.delete("/packages/{package_id}", status_code=status.HTTP_204_NO_CONTENT, dependencies=[Depends(require_permission("delete", "products"))])
async def delete_package(
    package_id: int,
    user_id: UserDep,
    service: PackageService = Depends(get_package_service),
) -> None:
    ok = await service.soft_delete(package_id, user_id)
    if not ok:
        raise NotFoundError("Упаковка не найдена")


@router.get("/product-locations", dependencies=[Depends(require_permission("view", "products"))])
async def list_product_locations(
    service: ProductLocationService = Depends(get_product_location_service),
):
    rows = await service.list_all()
    return [{"id": pl.id, "product_id": pl.product_id, "location_id": pl.location_id} for pl in rows]


@router.post("/product-locations", status_code=status.HTTP_201_CREATED, dependencies=[Depends(require_permission("create", "products"))])
async def create_product_location(
    body: ProductLocationCreate,
    service: ProductLocationService = Depends(get_product_location_service),
):
    pl = await service.create(**body.model_dump())
    return {"id": pl.id}


@router.get("/product-locations/{pl_id}", dependencies=[Depends(require_permission("view", "products"))])
async def get_product_location(
    pl_id: int,
    service: ProductLocationService = Depends(get_product_location_service),
):
    pl = await service.get_by_id(pl_id)
    if pl is None:
        raise NotFoundError("Связь не найдена")
    return {"id": pl.id, "product_id": pl.product_id, "location_id": pl.location_id}


@router.delete("/product-locations/{pl_id}", status_code=status.HTTP_204_NO_CONTENT, dependencies=[Depends(require_permission("delete", "products"))])
async def delete_product_location(
    pl_id: int,
    user_id: UserDep,
    service: ProductLocationService = Depends(get_product_location_service),
) -> None:
    ok = await service.soft_delete(pl_id, user_id)
    if not ok:
        raise NotFoundError("Связь не найдена")
