"""Фабрики сервисов склада."""

from __future__ import annotations

from fastapi import Depends

from app.api.deps import SessionDep
from app.orders.repository import (
    InboundOrderLineRepository,
    InboundOrderRepository,
    OutboundOrderLineRepository,
    OutboundOrderRepository,
)
from app.warehouse.repository import (
    BatchRepository,
    LocationRepository,
    LPNRepository,
    PackageRepository,
    ProductGroupRepository,
    ProductLocationRepository,
    ProductRepository,
    ReceivingDiscrepancyRepository,
    RowRepository,
    StockRepository,
    TaskLineRepository,
    TaskRepository,
    VirtualWarehouseRepository,
    WarehouseRepository,
    ZoneRepository,
)
from app.warehouse.services.batch_service import BatchService
from app.warehouse.services.lpn_service import LPNService
from app.warehouse.services.package_service import PackageService
from app.warehouse.services.placement_service import PlacementService
from app.warehouse.services.picking_service import PickingService
from app.warehouse.services.product_group_service import ProductGroupService
from app.warehouse.services.product_location_service import ProductLocationService
from app.warehouse.services.product_service import ProductService
from app.warehouse.services.receiving_service import ReceivingService
from app.warehouse.services.stock_service import StockService
from app.warehouse.services.task_service import TaskService
from app.warehouse.services.topology_service import (
    LocationService,
    RowService,
    VirtualWarehouseService,
    WarehouseService,
    ZoneService,
)


def get_product_service(session: SessionDep) -> ProductService:
    return ProductService(ProductRepository(session))


def get_product_group_service(session: SessionDep) -> ProductGroupService:
    return ProductGroupService(ProductGroupRepository(session))


def get_package_service(session: SessionDep) -> PackageService:
    return PackageService(PackageRepository(session))


def get_product_location_service(session: SessionDep) -> ProductLocationService:
    return ProductLocationService(ProductLocationRepository(session))


def get_batch_service(session: SessionDep) -> BatchService:
    return BatchService(BatchRepository(session))


def get_lpn_service(session: SessionDep) -> LPNService:
    return LPNService(LPNRepository(session))


def get_stock_service(session: SessionDep) -> StockService:
    return StockService(StockRepository(session))


def get_task_service(
    session: SessionDep,
    stock_service: StockService = Depends(get_stock_service),
) -> TaskService:
    return TaskService(
        TaskRepository(session),
        TaskLineRepository(session),
        stock_service,
    )


def get_receiving_service(
    session: SessionDep,
    stock_service: StockService = Depends(get_stock_service),
) -> ReceivingService:
    return ReceivingService(
        tasks=TaskRepository(session),
        lines=TaskLineRepository(session),
        inbound=InboundOrderRepository(session),
        inbound_lines=InboundOrderLineRepository(session),
        stock=stock_service,
        stock_repo=StockRepository(session),
        batches=BatchService(BatchRepository(session)),
        lpns=LPNService(LPNRepository(session)),
        products=ProductRepository(session),
        locations=LocationRepository(session),
        placement=PlacementService(session),
        discrepancies=ReceivingDiscrepancyRepository(session),
    )


def get_picking_service(
    session: SessionDep,
    stock_service: StockService = Depends(get_stock_service),
) -> PickingService:
    return PickingService(
        tasks=TaskRepository(session),
        lines=TaskLineRepository(session),
        outbound=OutboundOrderRepository(session),
        outbound_lines=OutboundOrderLineRepository(session),
        stock=stock_service,
        stock_repo=StockRepository(session),
    )


def get_warehouse_service(session: SessionDep) -> WarehouseService:
    return WarehouseService(WarehouseRepository(session))


def get_virtual_warehouse_service(session: SessionDep) -> VirtualWarehouseService:
    return VirtualWarehouseService(VirtualWarehouseRepository(session))


def get_zone_service(session: SessionDep) -> ZoneService:
    return ZoneService(ZoneRepository(session))


def get_row_service(session: SessionDep) -> RowService:
    return RowService(RowRepository(session))


def get_location_service(session: SessionDep) -> LocationService:
    return LocationService(LocationRepository(session))
