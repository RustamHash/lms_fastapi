"""API для топологии склада."""

from __future__ import annotations

from fastapi import APIRouter, Depends, status

from app.api.deps import Services, UserDep, require_permission
from app.api.v1.warehouse.schemas import (
    LocationCreate, LocationRead,
    RowCreate, RowRead,
    VirtualWarehouseCreate, VirtualWarehouseRead,
    WarehouseCreate, WarehouseRead,
    ZoneCreate, ZoneRead,
)
from app.core.exceptions import NotFoundError

router = APIRouter(prefix="/warehouse/topology", tags=["warehouse-topology"])


# ========== Склады ==========

@router.get("/warehouses", response_model=list[WarehouseRead], dependencies=[Depends(require_permission("view", "warehouse"))])
async def list_warehouses(services: Services) -> list[WarehouseRead]:
    from app.warehouse.repository import WarehouseRepository
    rows = await WarehouseRepository(services.product._repo._s).list_all()
    return [WarehouseRead.model_validate(r) for r in rows]


@router.post("/warehouses", response_model=WarehouseRead, status_code=status.HTTP_201_CREATED, dependencies=[Depends(require_permission("create", "warehouse"))])
async def create_warehouse(body: WarehouseCreate, services: Services, user_id: UserDep) -> WarehouseRead:
    from app.warehouse.repository import WarehouseRepository
    wh = await WarehouseRepository(services.product._repo._s).create(**body.model_dump())
    return WarehouseRead.model_validate(wh)


@router.get("/warehouses/{warehouse_id}", response_model=WarehouseRead, dependencies=[Depends(require_permission("view", "warehouse"))])
async def get_warehouse(warehouse_id: int, services: Services) -> WarehouseRead:
    from app.warehouse.repository import WarehouseRepository
    wh = await WarehouseRepository(services.product._repo._s).get_by_id(warehouse_id)
    if wh is None:
        raise NotFoundError("Склад не найден")
    return WarehouseRead.model_validate(wh)


@router.patch("/warehouses/{warehouse_id}", response_model=WarehouseRead, dependencies=[Depends(require_permission("update", "warehouse"))])
async def update_warehouse(warehouse_id: int, body: WarehouseCreate, services: Services, user_id: UserDep) -> WarehouseRead:
    from app.warehouse.repository import WarehouseRepository
    wh = await WarehouseRepository(services.product._repo._s).update(warehouse_id, **body.model_dump(exclude_unset=True))
    if wh is None:
        raise NotFoundError("Склад не найден")
    return WarehouseRead.model_validate(wh)


@router.delete("/warehouses/{warehouse_id}", status_code=status.HTTP_204_NO_CONTENT, dependencies=[Depends(require_permission("delete", "warehouse"))])
async def delete_warehouse(warehouse_id: int, services: Services, user_id: UserDep) -> None:
    from app.warehouse.repository import WarehouseRepository
    ok = await WarehouseRepository(services.product._repo._s).soft_delete(warehouse_id, user_id)
    if not ok:
        raise NotFoundError("Склад не найден")


# ========== Виртуальные склады ==========

@router.get("/virtual-warehouses", response_model=list[VirtualWarehouseRead], dependencies=[Depends(require_permission("view", "warehouse"))])
async def list_virtual_warehouses(services: Services) -> list[VirtualWarehouseRead]:
    from app.warehouse.repository import VirtualWarehouseRepository
    rows = await VirtualWarehouseRepository(services.product._repo._s).list_all()
    return [VirtualWarehouseRead.model_validate(r) for r in rows]


@router.post("/virtual-warehouses", response_model=VirtualWarehouseRead, status_code=status.HTTP_201_CREATED, dependencies=[Depends(require_permission("create", "warehouse"))])
async def create_virtual_warehouse(body: VirtualWarehouseCreate, services: Services, user_id: UserDep) -> VirtualWarehouseRead:
    from app.warehouse.repository import VirtualWarehouseRepository
    vw = await VirtualWarehouseRepository(services.product._repo._s).create(**body.model_dump())
    return VirtualWarehouseRead.model_validate(vw)


@router.get("/virtual-warehouses/{vw_id}", response_model=VirtualWarehouseRead, dependencies=[Depends(require_permission("view", "warehouse"))])
async def get_virtual_warehouse(vw_id: int, services: Services) -> VirtualWarehouseRead:
    from app.warehouse.repository import VirtualWarehouseRepository
    vw = await VirtualWarehouseRepository(services.product._repo._s).get_by_id(vw_id)
    if vw is None:
        raise NotFoundError("Виртуальный склад не найден")
    return VirtualWarehouseRead.model_validate(vw)


@router.patch("/virtual-warehouses/{vw_id}", response_model=VirtualWarehouseRead, dependencies=[Depends(require_permission("update", "warehouse"))])
async def update_virtual_warehouse(vw_id: int, body: VirtualWarehouseCreate, services: Services, user_id: UserDep) -> VirtualWarehouseRead:
    from app.warehouse.repository import VirtualWarehouseRepository
    vw = await VirtualWarehouseRepository(services.product._repo._s).update(vw_id, **body.model_dump(exclude_unset=True))
    if vw is None:
        raise NotFoundError("Виртуальный склад не найден")
    return VirtualWarehouseRead.model_validate(vw)


@router.delete("/virtual-warehouses/{vw_id}", status_code=status.HTTP_204_NO_CONTENT, dependencies=[Depends(require_permission("delete", "warehouse"))])
async def delete_virtual_warehouse(vw_id: int, services: Services, user_id: UserDep) -> None:
    from app.warehouse.repository import VirtualWarehouseRepository
    ok = await VirtualWarehouseRepository(services.product._repo._s).soft_delete(vw_id, user_id)
    if not ok:
        raise NotFoundError("Виртуальный склад не найден")


# ========== Зоны ==========

@router.get("/zones", response_model=list[ZoneRead], dependencies=[Depends(require_permission("view", "warehouse"))])
async def list_zones(services: Services) -> list[ZoneRead]:
    from app.warehouse.repository import ZoneRepository
    rows = await ZoneRepository(services.product._repo._s).list_all()
    return [ZoneRead.model_validate(r) for r in rows]


@router.post("/zones", response_model=ZoneRead, status_code=status.HTTP_201_CREATED, dependencies=[Depends(require_permission("create", "warehouse"))])
async def create_zone(body: ZoneCreate, services: Services, user_id: UserDep) -> ZoneRead:
    from app.warehouse.repository import ZoneRepository
    zone = await ZoneRepository(services.product._repo._s).create(**body.model_dump())
    return ZoneRead.model_validate(zone)


@router.get("/zones/{zone_id}", response_model=ZoneRead, dependencies=[Depends(require_permission("view", "warehouse"))])
async def get_zone(zone_id: int, services: Services) -> ZoneRead:
    from app.warehouse.repository import ZoneRepository
    zone = await ZoneRepository(services.product._repo._s).get_by_id(zone_id)
    if zone is None:
        raise NotFoundError("Зона не найдена")
    return ZoneRead.model_validate(zone)


@router.patch("/zones/{zone_id}", response_model=ZoneRead, dependencies=[Depends(require_permission("update", "warehouse"))])
async def update_zone(zone_id: int, body: ZoneCreate, services: Services, user_id: UserDep) -> ZoneRead:
    from app.warehouse.repository import ZoneRepository
    zone = await ZoneRepository(services.product._repo._s).update(zone_id, **body.model_dump(exclude_unset=True))
    if zone is None:
        raise NotFoundError("Зона не найдена")
    return ZoneRead.model_validate(zone)


@router.delete("/zones/{zone_id}", status_code=status.HTTP_204_NO_CONTENT, dependencies=[Depends(require_permission("delete", "warehouse"))])
async def delete_zone(zone_id: int, services: Services, user_id: UserDep) -> None:
    from app.warehouse.repository import ZoneRepository
    ok = await ZoneRepository(services.product._repo._s).soft_delete(zone_id, user_id)
    if not ok:
        raise NotFoundError("Зона не найдена")


# ========== Ряды ==========

@router.get("/rows", response_model=list[RowRead], dependencies=[Depends(require_permission("view", "warehouse"))])
async def list_rows(services: Services) -> list[RowRead]:
    from app.warehouse.repository import RowRepository
    rows = await RowRepository(services.product._repo._s).list_all()
    return [RowRead.model_validate(r) for r in rows]


@router.post("/rows", response_model=RowRead, status_code=status.HTTP_201_CREATED, dependencies=[Depends(require_permission("create", "warehouse"))])
async def create_row(body: RowCreate, services: Services, user_id: UserDep) -> RowRead:
    from app.warehouse.repository import RowRepository
    row = await RowRepository(services.product._repo._s).create(**body.model_dump())
    return RowRead.model_validate(row)


@router.get("/rows/{row_id}", response_model=RowRead, dependencies=[Depends(require_permission("view", "warehouse"))])
async def get_row(row_id: int, services: Services) -> RowRead:
    from app.warehouse.repository import RowRepository
    row = await RowRepository(services.product._repo._s).get_by_id(row_id)
    if row is None:
        raise NotFoundError("Ряд не найден")
    return RowRead.model_validate(row)


@router.patch("/rows/{row_id}", response_model=RowRead, dependencies=[Depends(require_permission("update", "warehouse"))])
async def update_row(row_id: int, body: RowCreate, services: Services, user_id: UserDep) -> RowRead:
    from app.warehouse.repository import RowRepository
    row = await RowRepository(services.product._repo._s).update(row_id, **body.model_dump(exclude_unset=True))
    if row is None:
        raise NotFoundError("Ряд не найден")
    return RowRead.model_validate(row)


@router.delete("/rows/{row_id}", status_code=status.HTTP_204_NO_CONTENT, dependencies=[Depends(require_permission("delete", "warehouse"))])
async def delete_row(row_id: int, services: Services, user_id: UserDep) -> None:
    from app.warehouse.repository import RowRepository
    ok = await RowRepository(services.product._repo._s).soft_delete(row_id, user_id)
    if not ok:
        raise NotFoundError("Ряд не найден")


# ========== Ячейки ==========

@router.get("/locations", response_model=list[LocationRead], dependencies=[Depends(require_permission("view", "warehouse"))])
async def list_locations(services: Services) -> list[LocationRead]:
    from app.warehouse.repository import LocationRepository
    rows = await LocationRepository(services.product._repo._s).list_all()
    return [LocationRead.model_validate(r) for r in rows]


@router.post("/locations", response_model=LocationRead, status_code=status.HTTP_201_CREATED, dependencies=[Depends(require_permission("create", "warehouse"))])
async def create_location(body: LocationCreate, services: Services, user_id: UserDep) -> LocationRead:
    from app.warehouse.repository import LocationRepository
    loc = await LocationRepository(services.product._repo._s).create(**body.model_dump())
    return LocationRead.model_validate(loc)


@router.get("/locations/{location_id}", response_model=LocationRead, dependencies=[Depends(require_permission("view", "warehouse"))])
async def get_location(location_id: int, services: Services) -> LocationRead:
    from app.warehouse.repository import LocationRepository
    loc = await LocationRepository(services.product._repo._s).get_by_id(location_id)
    if loc is None:
        raise NotFoundError("Ячейка не найдена")
    return LocationRead.model_validate(loc)


@router.patch("/locations/{location_id}", response_model=LocationRead, dependencies=[Depends(require_permission("update", "warehouse"))])
async def update_location(location_id: int, body: LocationCreate, services: Services, user_id: UserDep) -> LocationRead:
    from app.warehouse.repository import LocationRepository
    loc = await LocationRepository(services.product._repo._s).update(location_id, **body.model_dump(exclude_unset=True))
    if loc is None:
        raise NotFoundError("Ячейка не найдена")
    return LocationRead.model_validate(loc)


@router.delete("/locations/{location_id}", status_code=status.HTTP_204_NO_CONTENT, dependencies=[Depends(require_permission("delete", "warehouse"))])
async def delete_location(location_id: int, services: Services, user_id: UserDep) -> None:
    from app.warehouse.repository import LocationRepository
    ok = await LocationRepository(services.product._repo._s).soft_delete(location_id, user_id)
    if not ok:
        raise NotFoundError("Ячейка не найдена")
