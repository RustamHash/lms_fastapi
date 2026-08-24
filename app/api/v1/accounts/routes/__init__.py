"""Роутеры модуля accounts."""

from fastapi import APIRouter

from app.api.v1.accounts.routes.auth import router as auth_router
from app.api.v1.accounts.routes.users import router as users_router
from app.api.v1.accounts.routes.roles import router as roles_router
from app.api.v1.accounts.routes.audit import router as audit_router
from app.api.v1.accounts.routes.permissions import router as permissions_router
from app.api.v1.accounts.routes.user_settings import router as user_settings_router
from app.api.v1.accounts.routes.list_settings import router as list_settings_router

router = APIRouter()

router.include_router(auth_router)
router.include_router(users_router)
router.include_router(roles_router)
router.include_router(audit_router)
router.include_router(permissions_router)
router.include_router(user_settings_router)
router.include_router(list_settings_router)
