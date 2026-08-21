"""Middleware для приложения."""

from __future__ import annotations

import json
import logging

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response

from app.core.config import Settings
from app.core.security import decode_token_sub_user_id

logger = logging.getLogger(__name__)

# Методы, которые логируем
AUDIT_METHODS = {"POST", "PATCH", "PUT", "DELETE"}


class AuditMiddleware(BaseHTTPMiddleware):
    """Автоматический аудит действий пользователей."""

    async def dispatch(self, request: Request, call_next):
        # Пропускаем не-аудитируемые методы
        if request.method not in AUDIT_METHODS:
            return await call_next(request)

        # Извлекаем user_id из токена
        user_id = None
        auth_header = request.headers.get("authorization", "")
        if auth_header.startswith("Bearer "):
            token = auth_header[7:]
            try:
                user_id = decode_token_sub_user_id(token)
            except Exception:
                user_id = None

        # Копируем тело запроса (чтобы не потерять)
        body = None
        if request.method in ("POST", "PATCH", "PUT"):
            try:
                raw_body = await request.body()
                if raw_body:
                    body = json.loads(raw_body.decode("utf-8"))
            except Exception:
                body = None

        # Выполняем запрос
        response = await call_next(request)

        # Логируем только успешные (2xx) запросы
        if user_id and 200 <= response.status_code < 300:
            try:
                await self._log_audit(request, response, user_id, body)
            except Exception as e:
                logger.error("Ошибка записи аудита: %s", e)

        return response

    async def _log_audit(self, request: Request, response: Response, user_id: int, body: dict | None) -> None:
        """Записать в аудит."""
        from app.accounts.models import Audit
        from app.core.database import async_session_factory

        # Определяем action по методу
        action_map = {
            "POST": "create",
            "PATCH": "update",
            "PUT": "update",
            "DELETE": "delete",
        }
        action = action_map.get(request.method, "unknown")

        # Определяем entity_type из пути
        # /api/v1/products/5 → products
        path_parts = [p for p in request.url.path.split("/") if p]
        entity_type = path_parts[-1] if path_parts else "unknown"
        if entity_type.isdigit() and len(path_parts) > 1:
            entity_type = path_parts[-2]

        # Определяем entity_id из пути
        entity_id = None
        if len(path_parts) >= 2 and path_parts[-1].isdigit():
            entity_id = path_parts[-1]

        # Записываем
        async with async_session_factory() as session:
            audit = Audit(
                user_id=user_id,
                action=action,
                entity_type=entity_type,
                entity_id=entity_id,
                changes=body or {},
                ip_address=request.client.host if request.client else "",
                user_agent=request.headers.get("user-agent", ""),
            )
            session.add(audit)
            await session.commit()


def setup_middleware(app: FastAPI, settings: Settings) -> None:
    """Настройка middleware для приложения."""
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.add_middleware(AuditMiddleware)
