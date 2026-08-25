"""Роутеры модуля warehouse."""

from fastapi import APIRouter

from app.api.v1.warehouse.routes.products import router as products_router
from app.api.v1.warehouse.routes.batches import router as batches_router
from app.api.v1.warehouse.routes.lpns import router as lpns_router
from app.api.v1.warehouse.routes.stock import router as stock_router
from app.api.v1.warehouse.routes.tasks import router as tasks_router
from app.api.v1.warehouse.routes.topology import router as topology_router
from app.api.v1.warehouse.routes.receiving import router as receiving_router
from app.api.v1.warehouse.routes.picking import router as picking_router

router = APIRouter()

router.include_router(products_router)
router.include_router(batches_router)
router.include_router(lpns_router)
router.include_router(stock_router)
router.include_router(tasks_router)
router.include_router(receiving_router)
router.include_router(picking_router)
router.include_router(topology_router)
