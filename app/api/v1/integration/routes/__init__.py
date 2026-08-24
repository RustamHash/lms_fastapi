"""Роутеры модуля integration."""

from fastapi import APIRouter

from app.api.v1.integration.routes.profiles import router as profiles_router
from app.api.v1.integration.routes.imports import router as imports_router

router = APIRouter()

router.include_router(profiles_router)
router.include_router(imports_router)
