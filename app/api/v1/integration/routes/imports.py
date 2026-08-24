"""API для импорта."""

from __future__ import annotations

from fastapi import APIRouter

# Импортируем все из старого файла
from app.api.v1.integration.routes_import import router as imports_router

router = imports_router
