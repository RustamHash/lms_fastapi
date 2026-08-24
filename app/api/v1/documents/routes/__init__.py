"""Роутеры модуля documents."""

from fastapi import APIRouter

from app.api.v1.documents.routes.documents import router as documents_router

router = APIRouter()

router.include_router(documents_router)
