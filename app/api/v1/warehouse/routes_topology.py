"""API для топологии склада."""

from __future__ import annotations

from fastapi import HTTPException, APIRouter, Depends, status
from sqlalchemy import select

from app.api.deps import SessionDep, UserDep, require_permission
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
from app.warehouse.models import Location, Row, VirtualWarehouse, Warehouse, Zone
from app.warehouse.repository import (
    LocationRepository,
    RowRepository,
    VirtualWarehouseRepository,
    WarehouseRepository,
    ZoneRepository,
)

router = APIRouter(prefix="/warehouse/topology", tags=["warehouse-topology"])


# ========== Склады ==========

@router.get("/warehouses", response_model=list[WarehouseRead], dependencies=[Depends(require_permission("view", "warehouse"))])
async def list_warehouses(session: SessionDep) -> list[WarehouseRead]:
    rows = await WarehouseRepository(session).list_all()
    return [WarehouseRead.model_validate(r) for r in rows]


@router.post("/warehouses", response_model=WarehouseRead, status_code=status.HTTP_201_CREATED, dependencies=[Depends(require_permission("create", "warehouse"))])
async def create_warehouse(body: WarehouseCreate, session: SessionDep, user_id: UserDep) -> WarehouseRead:
    wh = Warehouse(created_by_id=user_id, **body.model_dump())
    session.add(wh)
    try:
        await session.flush()
    except Exception as e:
        await session.rollback()
        raise HTTPException(status_code=500, detail=f"Ошибка базы данных: {e}")
    return WarehouseRead.model_validate(wh)


@router.get("/warehouses/{warehouse_id}", response_model=WarehouseRead, dependencies=[Depends(require_permission("view", "warehouse"))])
async def get_warehouse(warehouse_id: int, session: SessionDep) -> WarehouseRead:
    wh = await WarehouseRepository(session).get_by_id(warehouse_id)
    if wh is None:
        raise NotFoundError("Склад не найден")
    return WarehouseRead.model_validate(wh)


@router.patch("/warehouses/{warehouse_id}", response_model=WarehouseRead, dependencies=[Depends(require_permission("update", "warehouse"))])
async def update_warehouse(warehouse_id: int, body: WarehouseCreate, session: SessionDep, user_id: UserDep) -> WarehouseRead:
    wh = await WarehouseRepository(session).get_by_id(warehouse_id)
    if wh is None:
        raise NotFoundError("Склад не найден")
    for field, value in body.model_dump(exclude_unset=True).items():
        setattr(wh, field, value)
    wh.updated_by_id = user_id
    try:
        await session.flush()
    except Exception as e:
        await session.rollback()
        raise HTTPException(status_code=500, detail=f"Ошибка базы данных: {e}")
    return WarehouseRead.model_validate(wh)


@router.delete("/warehouses/{warehouse_id}", status_code=status.HTTP_204_NO_CONTENT, dependencies=[Depends(require_permission("delete", "warehouse"))])
async def delete_warehouse(warehouse_id: int, session: SessionDep, user_id: UserDep) -> None:
    wh = await WarehouseRepository(session).get_by_id(warehouse_id)
    if wh is None:
        raise NotFoundError("Склад не найден")
    wh.soft_delete(user_id)
    try:
        await session.flush()
    except Exception as e:
        await session.rollback()
        raise HTTPException(status_code=500, detail=f"Ошибка базы данных: {e}")


# ========== Виртуальные склады ==========

@router.get("/virtual-warehouses", response_model=list[VirtualWarehouseRead], dependencies=[Depends(require_permission("view", "warehouse"))])
async def list_virtual_warehouses(session: SessionDep) -> list[VirtualWarehouseRead]:
    rows = await VirtualWarehouseRepository(session).list_all()
    return [VirtualWarehouseRead.model_validate(r) for r in rows]


@router.post("/virtual-warehouses", response_model=VirtualWarehouseRead, status_code=status.HTTP_201_CREATED, dependencies=[Depends(require_permission("create", "warehouse"))])
async def create_virtual_warehouse(body: VirtualWarehouseCreate, session: SessionDep, user_id: UserDep) -> VirtualWarehouseRead:
    vw = VirtualWarehouse(created_by_id=user_id, **body.model_dump())
    session.add(vw)
    try:
        await session.flush()
    except Exception as e:
        await session.rollback()
        raise HTTPException(status_code=500, detail=f"Ошибка базы данных: {e}")
    return VirtualWarehouseRead.model_validate(vw)


@router.get("/virtual-warehouses/{vw_id}", response_model=VirtualWarehouseRead, dependencies=[Depends(require_permission("view", "warehouse"))])
async def get_virtual_warehouse(vw_id: int, session: SessionDep) -> VirtualWarehouseRead:
    vw = await VirtualWarehouseRepository(session).get_by_id(vw_id)
    if vw is None:
        raise NotFoundError("Виртуальный склад не найден")
    return VirtualWarehouseRead.model_validate(vw)


@router.patch("/virtual-warehouses/{vw_id}", response_model=VirtualWarehouseRead, dependencies=[Depends(require_permission("update", "warehouse"))])
async def update_virtual_warehouse(vw_id: int, body: VirtualWarehouseCreate, session: SessionDep, user_id: UserDep) -> VirtualWarehouseRead:
    vw = await VirtualWarehouseRepository(session).get_by_id(vw_id)
    if vw is None:
        raise NotFoundError("Виртуальный склад не найден")
    for field, value in body.model_dump(exclude_unset=True).items():
        setattr(vw, field, value)
    vw.updated_by_id = user_id
    try:
        await session.flush()
    except Exception as e:
        await session.rollback()
        raise HTTPException(status_code=500, detail=f"Ошибка базы данных: {e}")
    return VirtualWarehouseRead.model_validate(vw)


@router.delete("/virtual-warehouses/{vw_id}", status_code=status.HTTP_204_NO_CONTENT, dependencies=[Depends(require_permission("delete", "warehouse"))])
async def delete_virtual_warehouse(vw_id: int, session: SessionDep, user_id: UserDep) -> None:
    vw = await VirtualWarehouseRepository(session).get_by_id(vw_id)
    if vw is None:
        raise NotFoundError("Виртуальный склад не найден")
    vw.soft_delete(user_id)
    try:
        await session.flush()
    except Exception as e:
        await session.rollback()
        raise HTTPException(status_code=500, detail=f"Ошибка базы данных: {e}")


# ========== Зоны ==========

@router.get("/zones", response_model=list[ZoneRead], dependencies=[Depends(require_permission("view", "warehouse"))])
async def list_zones(session: SessionDep) -> list[ZoneRead]:
    rows = await ZoneRepository(session).list_all()
    return [ZoneRead.model_validate(r) for r in rows]


@router.post("/zones", response_model=ZoneRead, status_code=status.HTTP_201_CREATED, dependencies=[Depends(require_permission("create", "warehouse"))])
async def create_zone(body: ZoneCreate, session: SessionDep, user_id: UserDep) -> ZoneRead:
    zone = Zone(created_by_id=user_id, **body.model_dump())
    session.add(zone)
    try:
        await session.flush()
    except Exception as e:
        await session.rollback()
        raise HTTPException(status_code=500, detail=f"Ошибка базы данных: {e}")
    return ZoneRead.model_validate(zone)


@router.get("/zones/{zone_id}", response_model=ZoneRead, dependencies=[Depends(require_permission("view", "warehouse"))])
async def get_zone(zone_id: int, session: SessionDep) -> ZoneRead:
    zone = await ZoneRepository(session).get_by_id(zone_id)
    if zone is None:
        raise NotFoundError("Зона не найдена")
    return ZoneRead.model_validate(zone)


@router.patch("/zones/{zone_id}", response_model=ZoneRead, dependencies=[Depends(require_permission("update", "warehouse"))])
async def update_zone(zone_id: int, body: ZoneCreate, session: SessionDep, user_id: UserDep) -> ZoneRead:
    zone = await ZoneRepository(session).get_by_id(zone_id)
    if zone is None:
        raise NotFoundError("Зона не найдена")
    for field, value in body.model_dump(exclude_unset=True).items():
        setattr(zone, field, value)
    zone.updated_by_id = user_id
    try:
        await session.flush()
    except Exception as e:
        await session.rollback()
        raise HTTPException(status_code=500, detail=f"Ошибка базы данных: {e}")
    return ZoneRead.model_validate(zone)


@router.delete("/zones/{zone_id}", status_code=status.HTTP_204_NO_CONTENT, dependencies=[Depends(require_permission("delete", "warehouse"))])
async def delete_zone(zone_id: int, session: SessionDep, user_id: UserDep) -> None:
    zone = await ZoneRepository(session).get_by_id(zone_id)
    if zone is None:
        raise NotFoundError("Зона не найдена")
    zone.soft_delete(user_id)
    try:
        await session.flush()
    except Exception as e:
        await session.rollback()
        raise HTTPException(status_code=500, detail=f"Ошибка базы данных: {e}")


# ========== Ряды ==========

@router.get("/rows", response_model=list[RowRead], dependencies=[Depends(require_permission("view", "warehouse"))])
async def list_rows(session: SessionDep) -> list[RowRead]:
    rows = await RowRepository(session).list_all()
    return [RowRead.model_validate(r) for r in rows]


@router.post("/rows", response_model=RowRead, status_code=status.HTTP_201_CREATED, dependencies=[Depends(require_permission("create", "warehouse"))])
async def create_row(body: RowCreate, session: SessionDep, user_id: UserDep) -> RowRead:
    row = Row(created_by_id=user_id, **body.model_dump())
    session.add(row)
    try:
        await session.flush()
    except Exception as e:
        await session.rollback()
        raise HTTPException(status_code=500, detail=f"Ошибка базы данных: {e}")
    return RowRead.model_validate(row)


@router.get("/rows/{row_id}", response_model=RowRead, dependencies=[Depends(require_permission("view", "warehouse"))])
async def get_row(row_id: int, session: SessionDep) -> RowRead:
    row = await RowRepository(session).get_by_id(row_id)
    if row is None:
        raise NotFoundError("Ряд не найден")
    return RowRead.model_validate(row)


@router.patch("/rows/{row_id}", response_model=RowRead, dependencies=[Depends(require_permission("update", "warehouse"))])
async def update_row(row_id: int, body: RowCreate, session: SessionDep, user_id: UserDep) -> RowRead:
    row = await RowRepository(session).get_by_id(row_id)
    if row is None:
        raise NotFoundError("Ряд не найден")
    for field, value in body.model_dump(exclude_unset=True).items():
        setattr(row, field, value)
    row.updated_by_id = user_id
    try:
        await session.flush()
    except Exception as e:
        await session.rollback()
        raise HTTPException(status_code=500, detail=f"Ошибка базы данных: {e}")
    return RowRead.model_validate(row)


@router.delete("/rows/{row_id}", status_code=status.HTTP_204_NO_CONTENT, dependencies=[Depends(require_permission("delete", "warehouse"))])
async def delete_row(row_id: int, session: SessionDep, user_id: UserDep) -> None:
    row = await RowRepository(session).get_by_id(row_id)
    if row is None:
        raise NotFoundError("Ряд не найден")
    row.soft_delete(user_id)
    try:
        await session.flush()
    except Exception as e:
        await session.rollback()
        raise HTTPException(status_code=500, detail=f"Ошибка базы данных: {e}")


# ========== Ячейки ==========

@router.get("/locations", response_model=list[LocationRead], dependencies=[Depends(require_permission("view", "warehouse"))])
async def list_locations(session: SessionDep) -> list[LocationRead]:
    rows = await LocationRepository(session).list_all()
    return [LocationRead.model_validate(r) for r in rows]


@router.post("/locations", response_model=LocationRead, status_code=status.HTTP_201_CREATED, dependencies=[Depends(require_permission("create", "warehouse"))])
async def create_location(body: LocationCreate, session: SessionDep, user_id: UserDep) -> LocationRead:
    loc = Location(created_by_id=user_id, **body.model_dump())
    session.add(loc)
    try:
        await session.flush()
    except Exception as e:
        await session.rollback()
        raise HTTPException(status_code=500, detail=f"Ошибка базы данных: {e}")
    return LocationRead.model_validate(loc)


@router.get("/locations/{location_id}", response_model=LocationRead, dependencies=[Depends(require_permission("view", "warehouse"))])
async def get_location(location_id: int, session: SessionDep) -> LocationRead:
    loc = await LocationRepository(session).get_by_id(location_id)
    if loc is None:
        raise NotFoundError("Ячейка не найдена")
    return LocationRead.model_validate(loc)


@router.patch("/locations/{location_id}", response_model=LocationRead, dependencies=[Depends(require_permission("update", "warehouse"))])
async def update_location(location_id: int, body: LocationCreate, session: SessionDep, user_id: UserDep) -> LocationRead:
    loc = await LocationRepository(session).get_by_id(location_id)
    if loc is None:
        raise NotFoundError("Ячейка не найдена")
    for field, value in body.model_dump(exclude_unset=True).items():
        setattr(loc, field, value)
    loc.updated_by_id = user_id
    try:
        await session.flush()
    except Exception as e:
        await session.rollback()
        raise HTTPException(status_code=500, detail=f"Ошибка базы данных: {e}")
    return LocationRead.model_validate(loc)


@router.delete("/locations/{location_id}", status_code=status.HTTP_204_NO_CONTENT, dependencies=[Depends(require_permission("delete", "warehouse"))])
async def delete_location(location_id: int, session: SessionDep, user_id: UserDep) -> None:
    loc = await LocationRepository(session).get_by_id(location_id)
    if loc is None:
        raise NotFoundError("Ячейка не найдена")
    loc.soft_delete(user_id)
    try:
        await session.flush()
    except Exception as e:
        await session.rollback()
        raise HTTPException(status_code=500, detail=f"Ошибка базы данных: {e}")
