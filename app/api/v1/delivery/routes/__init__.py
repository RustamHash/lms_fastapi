"""Роутеры модуля delivery."""

from fastapi import APIRouter

from app.api.v1.delivery.routes.orders import router as orders_router
from app.api.v1.delivery.routes.drivers import router as drivers_router
from app.api.v1.delivery.routes.vehicles import router as vehicles_router
from app.api.v1.delivery.routes.routes import router as routes_router
from app.api.v1.delivery.routes.deviations_lines import router as deviations_lines_router

router = APIRouter()

router.include_router(orders_router)
router.include_router(drivers_router)
router.include_router(vehicles_router)
router.include_router(routes_router)
router.include_router(deviations_lines_router)
