"""Middleware для приложения."""

from __future__ import annotations

import json
import logging
import time

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response

from app.core.config import Settings
from app.core.context import set_current_user_id
from app.core.security import (
    decode_token_is_portal_user,
    decode_token_sub_user_id,
)

logger = logging.getLogger(__name__)

AUDIT_METHODS = {"POST", "PATCH", "PUT", "DELETE"}

# Префиксы operator API, закрытые для portal-пользователей (клетка).
OPERATOR_API_PREFIX = "/api/v1"
PORTAL_API_PREFIX = "/api/v1/portal"
AUTH_API_PREFIX = "/api/v1/auth"


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Rate limit для /auth/ через Redis; fallback — in-memory на процесс."""

    def __init__(
        self,
        app,
        redis_url: str,
        max_requests: int = 10,
        window_seconds: int = 60,
    ):
        super().__init__(app)
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self._redis_url = redis_url
        self._redis = None
        self._local: dict[str, list[float]] = {}

    def _get_redis(self):
        if self._redis is False:
            return None
        if self._redis is not None:
            return self._redis
        try:
            import redis

            client = redis.Redis.from_url(self._redis_url, decode_responses=True)
            client.ping()
            self._redis = client
            return client
        except Exception as exc:
            logger.warning("Rate limit: Redis недоступен (%s), in-memory fallback", exc)
            self._redis = False
            return None

    def _allow_local(self, key: str) -> bool:
        now = time.time()
        times = [t for t in self._local.get(key, []) if now - t < self.window_seconds]
        if len(times) >= self.max_requests:
            self._local[key] = times
            return False
        times.append(now)
        self._local[key] = times
        return True

    def _allow_redis(self, client, key: str) -> bool:
        redis_key = f"ratelimit:auth:{key}"
        pipe = client.pipeline()
        pipe.incr(redis_key)
        pipe.expire(redis_key, self.window_seconds)
        count, _ = pipe.execute()
        return int(count) <= self.max_requests

    async def dispatch(self, request: Request, call_next):
        if "/auth/" not in request.url.path:
            return await call_next(request)

        client_ip = request.client.host if request.client else "unknown"
        client = self._get_redis()
        allowed = (
            self._allow_redis(client, client_ip)
            if client is not None
            else self._allow_local(client_ip)
        )
        if not allowed:
            return Response(
                status_code=429,
                content='{"detail": "Слишком много запросов. Попробуйте позже."}',
                media_type="application/json",
            )
        return await call_next(request)


class AuditMiddleware(BaseHTTPMiddleware):
    """Аудит mutating-запросов. Пишет в отдельную сессию с commit.

    Нельзя писать в request.state.session после call_next: UoW уже закрыт.
    """

    async def dispatch(self, request: Request, call_next):
        user_id = self._extract_user_id(request)
        # ContextVar нужен ORM defaults (created_by) на любой метод, не только mutating.
        set_current_user_id(user_id)

        if request.method not in AUDIT_METHODS:
            return await call_next(request)

        body = None
        if request.method in ("POST", "PATCH", "PUT"):
            try:
                raw_body = await request.body()
                if raw_body:
                    body = json.loads(raw_body.decode("utf-8"))
            except Exception:
                body = None

        response = await call_next(request)

        if user_id and 200 <= response.status_code < 300:
            try:
                await self._persist_audit(request, user_id, body)
            except Exception as e:
                logger.error("Ошибка записи аудита: %s", e, exc_info=True)

        return response

    @staticmethod
    def _extract_user_id(request: Request) -> int | None:
        auth_header = request.headers.get("authorization", "")
        if not auth_header.startswith("Bearer "):
            return None
        try:
            return decode_token_sub_user_id(auth_header[7:])
        except Exception:
            return None

    async def _persist_audit(
        self, request: Request, user_id: int, body: dict | None
    ) -> None:
        from app.accounts.models import Audit
        from app.core.database import async_session_factory

        action_map = {
            "POST": "create",
            "PATCH": "update",
            "PUT": "update",
            "DELETE": "delete",
        }
        action = action_map.get(request.method, "unknown")

        path_parts = [p for p in request.url.path.split("/") if p]
        entity_type = path_parts[-1] if path_parts else "unknown"
        if entity_type.isdigit() and len(path_parts) > 1:
            entity_type = path_parts[-2]

        entity_id = None
        if len(path_parts) >= 2 and path_parts[-1].isdigit():
            entity_id = path_parts[-1]

        audit = Audit(
            user_id=user_id,
            action=action,
            entity_type=entity_type,
            entity_id=entity_id,
            changes=body or {},
            ip_address=request.client.host if request.client else "",
            user_agent=request.headers.get("user-agent", "")[:512],
        )
        async with async_session_factory() as session:
            session.add(audit)
            await session.commit()


class PortalCageMiddleware(BaseHTTPMiddleware):
    """Пользователь портала не ходит в operator API — только /portal и /auth."""

    async def dispatch(self, request: Request, call_next):
        path = request.url.path
        if not path.startswith(OPERATOR_API_PREFIX):
            return await call_next(request)
        if path.startswith(PORTAL_API_PREFIX) or path.startswith(AUTH_API_PREFIX):
            return await call_next(request)

        auth_header = request.headers.get("authorization", "")
        if auth_header.startswith("Bearer "):
            token = auth_header[7:]
            if decode_token_is_portal_user(token):
                return Response(
                    status_code=403,
                    content='{"detail": "Доступ только через портал поклажедателя"}',
                    media_type="application/json",
                )
        return await call_next(request)


def setup_middleware(app: FastAPI, settings: Settings) -> None:
    """Настройка middleware для приложения."""
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.add_middleware(
        RateLimitMiddleware,
        redis_url=settings.redis_url,
    )
    app.add_middleware(PortalCageMiddleware)
    app.add_middleware(AuditMiddleware)
