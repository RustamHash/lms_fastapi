"""Главный роутер API v1."""

from fastapi import APIRouter

from app.api.v1.accounts.routes import router as accounts_router
from app.api.v1.accounts.routes_list import router as list_settings_router
from app.api.v1.delivery.routes import router as delivery_router
from app.api.v1.delivery.routes_deviations_lines import router as deviations_lines_router
from app.api.v1.documents.routes import router as documents_router
from app.api.v1.files.routes import router as files_router
from app.api.v1.integration.routes import router as integration_router
from app.api.v1.notifications.routes import router as notifications_router
from app.api.v1.orders.routes_inbound import router as inbound_orders_router
from app.api.v1.orders.routes_outbound import router as outbound_orders_router
from app.api.v1.orders.routes_return import router as return_orders_router
from app.api.v1.notifications.routes_rules import router as notification_rules_router
from app.api.v1.parties.routes import router as parties_router
from app.api.v1.parties.routes_delivery_zones import router as delivery_zones_router
from app.api.v1.parties.routes_carriers_keepers import router as carriers_keepers_router
from app.api.v1.warehouse.routes import router as warehouse_router
from app.api.v1.warehouse.routes_topology import router as warehouse_topology_router

api_router = APIRouter(prefix="/api/v1")

api_router.include_router(accounts_router)
api_router.include_router(list_settings_router)
api_router.include_router(parties_router)
api_router.include_router(delivery_zones_router)
api_router.include_router(carriers_keepers_router)
api_router.include_router(warehouse_router)
api_router.include_router(warehouse_topology_router)
api_router.include_router(documents_router)
api_router.include_router(delivery_router)
api_router.include_router(deviations_lines_router)
api_router.include_router(notifications_router)
api_router.include_router(inbound_orders_router)
api_router.include_router(outbound_orders_router)
api_router.include_router(return_orders_router)
api_router.include_router(notification_rules_router)
api_router.include_router(integration_router)
api_router.include_router(files_router)
