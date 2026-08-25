"""Точка входа FastAPI."""

import logging

logger = logging.getLogger(__name__)
from fastapi import FastAPI, Request
from fastapi.exceptions import HTTPException, ResponseValidationError
from pydantic import ValidationError
from fastapi.responses import JSONResponse

from app.api.v1.router import api_router
from app.core.config import get_settings
from app.core.model_rebuilder import rebuild_all_models
from app.core.middleware import setup_middleware
from app.infrastructure.logging import setup_logging
from app.core.init_db import init_db
from app.notifications.services.dispatcher import setup_notification_dispatcher

settings = get_settings()
setup_logging(settings)

logger.info("Environment: %s", settings.environment)
logger.info("Log level: %s", settings.log_level)
setup_notification_dispatcher(None)

app = FastAPI(title="LMS FastAPI")


logger = logging.getLogger(__name__)


@app.exception_handler(ResponseValidationError)
async def response_validation_exception_handler(
    request: Request, exc: ResponseValidationError
) -> JSONResponse:
    """Обработчик ошибок валидации ответа (response_model)."""
    logger.error(
        "Response Validation Error on path %s | Method: %s",
        request.url.path,
        request.method,
    )
    return JSONResponse(
        status_code=500,
        content={"detail": "Ошибка валидации ответа"},
    )


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Глобальный обработчик необработанных исключений."""
    logger.error(
        "Unhandled exception: %s | Path: %s | Method: %s",
        exc,
        request.url.path,
        request.method,
        exc_info=True,
    )
    return JSONResponse(
        status_code=500,
        content={
            "detail": "Внутренняя ошибка сервера",
            "error_type": exc.__class__.__name__,
        },
    )


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    """Обработчик HTTP-исключений с логированием."""
    logger.warning(
        "HTTP %s: %s | Path: %s",
        exc.status_code,
        exc.detail,
        request.url.path,
    )
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail},
    )


@app.exception_handler(ValidationError)
async def validation_exception_handler(
    request: Request, exc: ValidationError
) -> JSONResponse:
    """Обработчик ошибок валидации Pydantic."""
    logger.warning(
        "Validation error: %s | Path: %s",
        exc.errors(include_url=False, include_input=False),
        request.url.path,
    )
    return JSONResponse(
        status_code=422,
        content={"detail": exc.errors(include_url=False, include_input=False)},
    )


# Пересборка Pydantic-моделей для решения циклических зависимостей
rebuild_all_models()

# Middleware
setup_middleware(app, settings)

# Роутер
app.include_router(api_router)


@app.on_event("startup")
async def startup_event():
    """Инициализация при старте."""
    from app.core.database import async_session_factory

    async with async_session_factory() as session:
        await init_db(session)


from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pathlib import Path

# Раздача фронтенда (только если собран)
frontend_dist = Path(__file__).parent.parent / "frontend" / "dist"

if frontend_dist.exists() and (frontend_dist / "assets").exists():
    app.mount("/assets", StaticFiles(directory=frontend_dist / "assets"), name="assets")

    @app.get("/{full_path:path}")
    async def serve_frontend(full_path: str):
        file_path = frontend_dist / full_path
        if file_path.exists() and file_path.is_file():
            return FileResponse(file_path)
        return FileResponse(frontend_dist / "index.html")

else:
    logger.info("Фронтенд не собран — работаем в dev-режиме (только API)")
