"""Точка входа FastAPI."""

from fastapi import FastAPI

from app.api.v1.router import api_router
from app.core.config import get_settings
from app.infrastructure.logging import setup_logging

settings = get_settings()
setup_logging(settings)

app = FastAPI(title="LMS FastAPI")
app.include_router(api_router)
