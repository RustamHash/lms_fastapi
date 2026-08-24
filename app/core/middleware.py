"""Middleware для приложения."""

from __future__ import annotations

import json
import logging

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response

from app.core.config import Settings
from app.core.context import set_current_user_id
from app.core.security import decode_token_sub_user_id

logger = logging.getLogger(__name__)

# Методы, которые логируем
AUDIT_METHODS = {"POST", "PATCH", "PUT", "DELETE"}


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Простой rate limiting для auth-эндпоинтов."""

    def __init__(self, app, max_requests: int = 10, window_seconds: int = 60):
        super().__init__(app)
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self._requests = {}

    async def dispatch(self, request: Request, call_next):
        # Применяем только к auth-эндпоинтам
        if "/auth/" in request.url.path:
            client_ip = request.client.host if request.client else "unknown"
            current_time = __import__("time").time()

            # Очистка старых записей
            self._requests = {
                ip: [t for t in times if current_time - t < self.window_seconds]
                for ip, times in self._requests.items()
            }

            # Проверка лимита
            times = self._requests.get(client_ip, [])
            if len(times) >= self.max_requests:
                return Response(
                    status_code=429,
                    content='{"detail": "Слишком много запросов. Попробуйте позже."}',
                    media_type="application/json",
                )

            # Запоминаем запрос
            times.append(current_time)
            self._requests[client_ip] = times

        return await call_next(request)


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

        # Устанавливаем текущего пользователя в контекст
        set_current_user_id(user_id)

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
                # Получаем сессию из request.state (если есть)
                session = getattr(request.state, "session", None)

                if session is not None:
                    # Используем ту же сессию, что и основной запрос
                    await self._write_audit(session, request, user_id, body)
                else:
                    # Fallback: если сессии нет — создаем свою
                    from app.core.database import async_session_factory

                    async with async_session_factory() as session:
                        await self._write_audit(session, request, user_id, body)
            except Exception as e:
                logger.error("Ошибка записи аудита: %s", e, exc_info=True)

        return response

    async def _write_audit(
        self, session, request: Request, user_id: int, body: dict | None
    ) -> None:
        """Создать запись аудита в переданной сессии."""
        from app.accounts.models import Audit

        # Определяем action по методу
        action_map = {
            "POST": "create",
            "PATCH": "update",
            "PUT": "update",
            "DELETE": "delete",
        }
        action = action_map.get(request.method, "unknown")

        # Определяем entity_type из пути
        path_parts = [p for p in request.url.path.split("/") if p]
        entity_type = path_parts[-1] if path_parts else "unknown"
        if entity_type.isdigit() and len(path_parts) > 1:
            entity_type = path_parts[-2]

        # Определяем entity_id из пути
        entity_id = None
        if len(path_parts) >= 2 and path_parts[-1].isdigit():
            entity_id = path_parts[-1]

        # Записываем в переданную сессию (без commit — UoW сделает)
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


def setup_middleware(app: FastAPI, settings: Settings) -> None:
    """Настройка middleware для приложения."""
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.add_middleware(RateLimitMiddleware)
    app.add_middleware(AuditMiddleware)
