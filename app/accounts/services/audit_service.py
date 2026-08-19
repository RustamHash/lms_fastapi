"""Сервис аудита."""

from __future__ import annotations

from app.accounts.models import Audit
from app.accounts.repository import AuditRepository


class AuditService:
    def __init__(self, repo: AuditRepository) -> None:
        self._repo = repo

    async def log(
        self,
        user_id: int | None,
        action: str,
        entity_type: str,
        entity_id: str | None = None,
        changes: dict | None = None,
        request=None,
    ) -> Audit:
        return await self._repo.create(
            user_id=user_id,
            action=action,
            entity_type=entity_type,
            entity_id=str(entity_id) if entity_id else None,
            changes=changes or {},
            ip_address=request.headers.get("x-forwarded-for", "") if request else "",
            user_agent=request.headers.get("user-agent", "") if request else "",
        )

    async def list_by_user(self, user_id: int, limit: int = 100) -> list[Audit]:
        return await self._repo.list_by_user(user_id, limit)
