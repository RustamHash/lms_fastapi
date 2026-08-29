"""API для топологии склада.

Политика доступа: топология (склады/зоны/ячейки) — общая для операторов склада,
ограничивается только RBAC (view/create/… warehouse). Виртуальные склады
привязаны к depositor_id, но оператор видит все; portal-пользователи к этим
эндпоинтам не допускаются (PortalCageMiddleware).
"""

from __future__ import annotations

from fastapi import APIRouter, Depends, status

from app.api.deps import UserDep, require_permission
from app.api.v1.warehouse.deps import (
    get_location_service,
    get_row_service,
    get_virtual_warehouse_service,
    get_warehouse_service,
    get_zone_service,
)
from app.api.v1.warehouse.schemas import (
    LocationCreate,
    LocationRead,
    RowCreate,
    RowRead,
    VirtualWarehouseCreate,
    VirtualWarehouseRead,
    WarehouseCreate,
    WarehouseRead,
    ZoneCreate,
    ZoneRead,
)
from app.core.exceptions import NotFoundError
from app.warehouse.services.topology_service import (
    LocationService,
    RowService,
    VirtualWarehouseService,
    WarehouseService,
    ZoneService,
)

router = APIRouter(prefix="/warehouse/topology", tags=["warehouse-topology"])


@router.get("/warehouses", response_model=list[WarehouseRead], dependencies=[Depends(require_permission("view", "warehouse"))])
async def list_warehouses(
    service: WarehouseService = Depends(get_warehouse_service),
) -> list[WarehouseRead]:
    rows = await service.list_all()
    return [WarehouseRead.model_validate(r) for r in rows]


@router.post("/warehouses", response_model=WarehouseRead, status_code=status.HTTP_201_CREATED, dependencies=[Depends(require_permission("create", "warehouse"))])
async def create_warehouse(
    body: WarehouseCreate,
    service: WarehouseService = Depends(get_warehouse_service),
) -> WarehouseRead:
    return WarehouseRead.model_validate(await service.create(**body.model_dump()))


@router.get("/warehouses/{warehouse_id}", response_model=WarehouseRead, dependencies=[Depends(require_permission("view", "warehouse"))])
async def get_warehouse(
    warehouse_id: int,
    service: WarehouseService = Depends(get_warehouse_service),
) -> WarehouseRead:
    wh = await service.get_by_id(warehouse_id)
    if wh is None:
        raise NotFoundError("Склад не найден")
    return WarehouseRead.model_validate(wh)


@router.patch("/warehouses/{warehouse_id}", response_model=WarehouseRead, dependencies=[Depends(require_permission("update", "warehouse"))])
async def update_warehouse(
    warehouse_id: int,
    body: WarehouseCreate,
    service: WarehouseService = Depends(get_warehouse_service),
) -> WarehouseRead:
    wh = await service.update(warehouse_id, **body.model_dump(exclude_unset=True))
    if wh is None:
        raise NotFoundError("Склад не найден")
    return WarehouseRead.model_validate(wh)


@router.delete("/warehouses/{warehouse_id}", status_code=status.HTTP_204_NO_CONTENT, dependencies=[Depends(require_permission("delete", "warehouse"))])
async def delete_warehouse(
    warehouse_id: int,
    user_id: UserDep,
    service: WarehouseService = Depends(get_warehouse_service),
) -> None:
    ok = await service.soft_delete(warehouse_id, user_id)
    if not ok:
        raise NotFoundError("Склад не найден")


@router.get("/virtual-warehouses", response_model=list[VirtualWarehouseRead], dependencies=[Depends(require_permission("view", "warehouse"))])
async def list_virtual_warehouses(
    service: VirtualWarehouseService = Depends(get_virtual_warehouse_service),
) -> list[VirtualWarehouseRead]:
    rows = await service.list_all()
    return [VirtualWarehouseRead.model_validate(r) for r in rows]


@router.post("/virtual-warehouses", response_model=VirtualWarehouseRead, status_code=status.HTTP_201_CREATED, dependencies=[Depends(require_permission("create", "warehouse"))])
async def create_virtual_warehouse(
    body: VirtualWarehouseCreate,
    service: VirtualWarehouseService = Depends(get_virtual_warehouse_service),
) -> VirtualWarehouseRead:
    return VirtualWarehouseRead.model_validate(await service.create(**body.model_dump()))


@router.get("/virtual-warehouses/{vw_id}", response_model=VirtualWarehouseRead, dependencies=[Depends(require_permission("view", "warehouse"))])
async def get_virtual_warehouse(
    vw_id: int,
    service: VirtualWarehouseService = Depends(get_virtual_warehouse_service),
) -> VirtualWarehouseRead:
    vw = await service.get_by_id(vw_id)
    if vw is None:
        raise NotFoundError("Виртуальный склад не найден")
    return VirtualWarehouseRead.model_validate(vw)


@router.patch("/virtual-warehouses/{vw_id}", response_model=VirtualWarehouseRead, dependencies=[Depends(require_permission("update", "warehouse"))])
async def update_virtual_warehouse(
    vw_id: int,
    body: VirtualWarehouseCreate,
    service: VirtualWarehouseService = Depends(get_virtual_warehouse_service),
) -> VirtualWarehouseRead:
    vw = await service.update(vw_id, **body.model_dump(exclude_unset=True))
    if vw is None:
        raise NotFoundError("Виртуальный склад не найден")
    return VirtualWarehouseRead.model_validate(vw)


@router.delete("/virtual-warehouses/{vw_id}", status_code=status.HTTP_204_NO_CONTENT, dependencies=[Depends(require_permission("delete", "warehouse"))])
async def delete_virtual_warehouse(
    vw_id: int,
    user_id: UserDep,
    service: VirtualWarehouseService = Depends(get_virtual_warehouse_service),
) -> None:
    ok = await service.soft_delete(vw_id, user_id)
    if not ok:
        raise NotFoundError("Виртуальный склад не найден")


@router.get("/zones", response_model=list[ZoneRead], dependencies=[Depends(require_permission("view", "warehouse"))])
async def list_zones(service: ZoneService = Depends(get_zone_service)) -> list[ZoneRead]:
    rows = await service.list_all()
    return [ZoneRead.model_validate(r) for r in rows]


@router.post("/zones", response_model=ZoneRead, status_code=status.HTTP_201_CREATED, dependencies=[Depends(require_permission("create", "warehouse"))])
async def create_zone(
    body: ZoneCreate,
    service: ZoneService = Depends(get_zone_service),
) -> ZoneRead:
    return ZoneRead.model_validate(await service.create(**body.model_dump()))


@router.get("/zones/{zone_id}", response_model=ZoneRead, dependencies=[Depends(require_permission("view", "warehouse"))])
async def get_zone(zone_id: int, service: ZoneService = Depends(get_zone_service)) -> ZoneRead:
    zone = await service.get_by_id(zone_id)
    if zone is None:
        raise NotFoundError("Зона не найдена")
    return ZoneRead.model_validate(zone)


@router.patch("/zones/{zone_id}", response_model=ZoneRead, dependencies=[Depends(require_permission("update", "warehouse"))])
async def update_zone(
    zone_id: int,
    body: ZoneCreate,
    service: ZoneService = Depends(get_zone_service),
) -> ZoneRead:
    zone = await service.update(zone_id, **body.model_dump(exclude_unset=True))
    if zone is None:
        raise NotFoundError("Зона не найдена")
    return ZoneRead.model_validate(zone)


@router.delete("/zones/{zone_id}", status_code=status.HTTP_204_NO_CONTENT, dependencies=[Depends(require_permission("delete", "warehouse"))])
async def delete_zone(
    zone_id: int,
    user_id: UserDep,
    service: ZoneService = Depends(get_zone_service),
) -> None:
    ok = await service.soft_delete(zone_id, user_id)
    if not ok:
        raise NotFoundError("Зона не найдена")


@router.get("/rows", response_model=list[RowRead], dependencies=[Depends(require_permission("view", "warehouse"))])
async def list_rows(service: RowService = Depends(get_row_service)) -> list[RowRead]:
    rows = await service.list_all()
    return [RowRead.model_validate(r) for r in rows]


@router.post("/rows", response_model=RowRead, status_code=status.HTTP_201_CREATED, dependencies=[Depends(require_permission("create", "warehouse"))])
async def create_row(
    body: RowCreate,
    service: RowService = Depends(get_row_service),
) -> RowRead:
    return RowRead.model_validate(await service.create(**body.model_dump()))


@router.get("/rows/{row_id}", response_model=RowRead, dependencies=[Depends(require_permission("view", "warehouse"))])
async def get_row(row_id: int, service: RowService = Depends(get_row_service)) -> RowRead:
    row = await service.get_by_id(row_id)
    if row is None:
        raise NotFoundError("Ряд не найден")
    return RowRead.model_validate(row)


@router.patch("/rows/{row_id}", response_model=RowRead, dependencies=[Depends(require_permission("update", "warehouse"))])
async def update_row(
    row_id: int,
    body: RowCreate,
    service: RowService = Depends(get_row_service),
) -> RowRead:
    row = await service.update(row_id, **body.model_dump(exclude_unset=True))
    if row is None:
        raise NotFoundError("Ряд не найден")
    return RowRead.model_validate(row)


@router.delete("/rows/{row_id}", status_code=status.HTTP_204_NO_CONTENT, dependencies=[Depends(require_permission("delete", "warehouse"))])
async def delete_row(
    row_id: int,
    user_id: UserDep,
    service: RowService = Depends(get_row_service),
) -> None:
    ok = await service.soft_delete(row_id, user_id)
    if not ok:
        raise NotFoundError("Ряд не найден")


@router.get("/locations", response_model=list[LocationRead], dependencies=[Depends(require_permission("view", "warehouse"))])
async def list_locations(
    service: LocationService = Depends(get_location_service),
) -> list[LocationRead]:
    rows = await service.list_all()
    return [LocationRead.model_validate(r) for r in rows]


@router.post("/locations", response_model=LocationRead, status_code=status.HTTP_201_CREATED, dependencies=[Depends(require_permission("create", "warehouse"))])
async def create_location(
    body: LocationCreate,
    service: LocationService = Depends(get_location_service),
) -> LocationRead:
    return LocationRead.model_validate(await service.create(**body.model_dump()))


@router.get("/locations/{location_id}", response_model=LocationRead, dependencies=[Depends(require_permission("view", "warehouse"))])
async def get_location(
    location_id: int,
    service: LocationService = Depends(get_location_service),
) -> LocationRead:
    loc = await service.get_by_id(location_id)
    if loc is None:
        raise NotFoundError("Ячейка не найдена")
    return LocationRead.model_validate(loc)


@router.patch("/locations/{location_id}", response_model=LocationRead, dependencies=[Depends(require_permission("update", "warehouse"))])
async def update_location(
    location_id: int,
    body: LocationCreate,
    service: LocationService = Depends(get_location_service),
) -> LocationRead:
    loc = await service.update(location_id, **body.model_dump(exclude_unset=True))
    if loc is None:
        raise NotFoundError("Ячейка не найдена")
    return LocationRead.model_validate(loc)


@router.delete("/locations/{location_id}", status_code=status.HTTP_204_NO_CONTENT, dependencies=[Depends(require_permission("delete", "warehouse"))])
async def delete_location(
    location_id: int,
    user_id: UserDep,
    service: LocationService = Depends(get_location_service),
) -> None:
    ok = await service.soft_delete(location_id, user_id)
    if not ok:
        raise NotFoundError("Ячейка не найдена")
