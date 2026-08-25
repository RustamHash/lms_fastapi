# app/api/v1/router.py

"""Главный роутер API v1."""

from fastapi import APIRouter

api_router = APIRouter(prefix="/api/v1")

# ========== Модули ==========
from app.api.v1.parties.routes import router as parties_router
from app.api.v1.accounts.routes import router as accounts_router
from app.api.v1.warehouse.routes import router as warehouse_router
from app.api.v1.orders.routes import router as orders_router
from app.api.v1.delivery.routes import router as delivery_router
from app.api.v1.documents.routes import router as documents_router
from app.api.v1.notifications.routes import router as notifications_router
from app.api.v1.integration.routes import router as integration_router
from app.files.routes import router as files_router

api_router.include_router(parties_router)
api_router.include_router(accounts_router)
api_router.include_router(warehouse_router)
api_router.include_router(orders_router)
api_router.include_router(delivery_router)
api_router.include_router(documents_router)
api_router.include_router(notifications_router)
api_router.include_router(integration_router)
api_router.include_router(files_router)

# Метаданные
from app.api.v1.meta import router as meta_router
api_router.include_router(meta_router)
