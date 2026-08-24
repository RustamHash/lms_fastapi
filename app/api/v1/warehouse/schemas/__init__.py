"""Схемы модуля warehouse."""

from app.api.v1.warehouse.schemas.products import (
    ProductRead,
    ProductCreate,
    ProductGroupCreate,
    PackageCreate,
    ProductLocationCreate,
)
from app.api.v1.warehouse.schemas.batches import BatchRead, BatchCreate
from app.api.v1.warehouse.schemas.lpns import LPNRead, LPNCreate
from app.api.v1.warehouse.schemas.stock import (
    StockBalanceRead,
    StockAdd,
    StockRemove,
    StockMove,
)
from app.api.v1.warehouse.schemas.tasks import (
    TaskRead,
    TaskCreate,
    TaskLineAdd,
    PickingTaskCreate,
    TaskUpdate,
    TaskComplete,
    TaskLineComplete,
    TaskList,
    TaskDetail,
)
from app.api.v1.warehouse.schemas.topology import (
    WarehouseRead,
    WarehouseCreate,
    VirtualWarehouseRead,
    VirtualWarehouseCreate,
    ZoneRead,
    ZoneCreate,
    RowRead,
    RowCreate,
    LocationRead,
    LocationCreate,
)

__all__ = [
    # Products
    "ProductRead",
    "ProductCreate",
    "ProductGroupCreate",
    "PackageCreate",
    "ProductLocationCreate",
    # Batches
    "BatchRead",
    "BatchCreate",
    # LPNs
    "LPNRead",
    "LPNCreate",
    # Stock
    "StockBalanceRead",
    "StockAdd",
    "StockRemove",
    "StockMove",
    # Tasks
    "TaskRead",
    "TaskCreate",
    "TaskLineAdd",
    "PickingTaskCreate",
    "TaskUpdate",
    "TaskComplete",
    "TaskLineComplete",
    "TaskList",
    "TaskDetail",
    # Topology
    "WarehouseRead",
    "WarehouseCreate",
    "VirtualWarehouseRead",
    "VirtualWarehouseCreate",
    "ZoneRead",
    "ZoneCreate",
    "RowRead",
    "RowCreate",
    "LocationRead",
    "LocationCreate",
]
