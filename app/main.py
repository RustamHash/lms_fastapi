"""Точка входа FastAPI."""

from fastapi import FastAPI

from app.api.v1.router import api_router
from app.core.config import get_settings
from app.core.middleware import setup_middleware
from app.infrastructure.logging import setup_logging
from app.notifications.services.dispatcher import setup_notification_dispatcher

settings = get_settings()
setup_logging(settings)
# Подписка на события (диспетчер уведомлений)
setup_notification_dispatcher(None)

app = FastAPI(title="LMS FastAPI")
setup_middleware(app, settings)
app.include_router(api_router)


from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pathlib import Path

# Раздача фронтенда
frontend_dist = Path(__file__).parent.parent / "frontend" / "dist"

if frontend_dist.exists():
    app.mount("/assets", StaticFiles(directory=frontend_dist / "assets"), name="assets")

    @app.get("/{full_path:path}")
    async def serve_frontend(full_path: str):
        file_path = frontend_dist / full_path
        if file_path.exists() and file_path.is_file():
            return FileResponse(file_path)
        return FileResponse(frontend_dist / "index.html")
