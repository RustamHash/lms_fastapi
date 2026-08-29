"""Точка входа FastAPI."""

from __future__ import annotations

import logging
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError, ResponseValidationError
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

from app.api.v1.router import api_router
from app.core.config import get_settings
from app.core.middleware import setup_middleware
from app.core.model_rebuilder import rebuild_all_models
from app.infrastructure.bootstrap_workers import bootstrap_background_subscribers
from app.infrastructure.logging import setup_logging

settings = get_settings()
setup_logging(settings)
logger = logging.getLogger(__name__)
logger.info("Environment: %s", settings.environment)
logger.info("Log level: %s", settings.log_level)

_SPA_RESERVED_PREFIXES = ("api", "docs", "redoc", "openapi.json", "health")


@asynccontextmanager
async def lifespan(_app: FastAPI):
    """Подписчики event_bus и rebuild схем — на старте процесса, не при import."""
    bootstrap_background_subscribers()
    rebuild_all_models()
    yield


app = FastAPI(title="LMS FastAPI", lifespan=lifespan)


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}


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


@app.exception_handler(RequestValidationError)
async def request_validation_exception_handler(
    request: Request, exc: RequestValidationError
) -> JSONResponse:
    """Ошибки валидации тела/параметров запроса → 422."""
    detail = [
        {k: v for k, v in err.items() if k != "url"} for err in exc.errors()
    ]
    logger.warning("Validation error: %s | Path: %s", detail, request.url.path)
    return JSONResponse(status_code=422, content={"detail": detail})


@app.exception_handler(ResponseValidationError)
async def response_validation_exception_handler(
    request: Request, exc: ResponseValidationError
) -> JSONResponse:
    """Обработчик ошибок валидации ответа (response_model)."""
    logger.error(
        "Response Validation Error on path %s | Method: %s | errors: %s",
        request.url.path,
        request.method,
        exc.errors(),
        exc_info=True,
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
    content: dict[str, str] = {"detail": "Внутренняя ошибка сервера"}
    if settings.environment != "production":
        content["error_type"] = exc.__class__.__name__
    return JSONResponse(status_code=500, content=content)


setup_middleware(app, settings)
app.include_router(api_router)

frontend_dist = Path(__file__).resolve().parent.parent / "frontend" / "dist"

if frontend_dist.exists() and (frontend_dist / "assets").exists():
    app.mount("/assets", StaticFiles(directory=frontend_dist / "assets"), name="assets")

    @app.get("/{full_path:path}")
    async def serve_frontend(full_path: str):
        head = full_path.split("/", 1)[0] if full_path else ""
        if head in _SPA_RESERVED_PREFIXES or full_path in _SPA_RESERVED_PREFIXES:
            return JSONResponse(status_code=404, content={"detail": "Not Found"})

        file_path = frontend_dist / full_path
        if file_path.exists() and file_path.is_file():
            return FileResponse(file_path)
        return FileResponse(frontend_dist / "index.html")

else:
    logger.info("Фронтенд не собран — работаем в dev-режиме (только API)")
