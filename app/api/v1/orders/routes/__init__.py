"""Роутеры модуля orders."""

from fastapi import APIRouter

from app.api.v1.orders.routes.inbound import router as inbound_router
from app.api.v1.orders.routes.outbound import router as outbound_router
from app.api.v1.orders.routes.returns import router as returns_router

router = APIRouter()

router.include_router(inbound_router)
router.include_router(outbound_router)
router.include_router(returns_router)
