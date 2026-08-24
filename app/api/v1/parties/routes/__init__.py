"""Роутеры модуля parties."""

from fastapi import APIRouter

from app.api.v1.parties.routes.addresses import router as addresses_router
from app.api.v1.parties.routes.raw_addresses import router as raw_addresses_router
from app.api.v1.parties.routes.legal_entities import router as legal_entities_router
from app.api.v1.parties.routes.depositors import router as depositors_router
from app.api.v1.parties.routes.clients import router as clients_router
from app.api.v1.parties.routes.contracts import router as contracts_router
from app.api.v1.parties.routes.tariffs import router as tariffs_router
from app.api.v1.parties.routes.tariff_documents import router as tariff_documents_router
from app.api.v1.parties.routes.delivery_zones import router as delivery_zones_router
from app.api.v1.parties.routes.carriers import router as carriers_router
from app.api.v1.parties.routes.keepers import router as keepers_router

router = APIRouter()

router.include_router(addresses_router)
router.include_router(raw_addresses_router)
router.include_router(legal_entities_router)
router.include_router(depositors_router)
router.include_router(clients_router)
router.include_router(contracts_router)
router.include_router(tariffs_router)
router.include_router(tariff_documents_router)
router.include_router(delivery_zones_router)
router.include_router(carriers_router)
router.include_router(keepers_router)
