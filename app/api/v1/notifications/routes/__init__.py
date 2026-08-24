"""Роутеры модуля notifications."""

from fastapi import APIRouter

from app.api.v1.notifications.routes.notifications import router as notifications_router
from app.api.v1.notifications.routes.rules import router as rules_router

router = APIRouter()

router.include_router(notifications_router)
router.include_router(rules_router)
