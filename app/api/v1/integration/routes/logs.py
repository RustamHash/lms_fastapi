"""Список и карточка журнала импорта."""

from __future__ import annotations

from fastapi import APIRouter, Depends

from app.api.deps import Services, require_permission
from app.api.v1.integration.schemas.logs import IntegrationLogRead
from app.core.exceptions import NotFoundError
from app.integration.repository import IntegrationLogRepository

router = APIRouter(prefix="/integrations", tags=["integrations"])


@router.get(
    "/logs",
    response_model=list[IntegrationLogRead],
    dependencies=[Depends(require_permission("view", "integrations"))],
)
async def list_logs(services: Services) -> list[IntegrationLogRead]:
    rows = await IntegrationLogRepository(services.session).list_all()
    return [IntegrationLogRead.model_validate(r) for r in rows]


@router.get(
    "/logs/{log_id}",
    response_model=IntegrationLogRead,
    dependencies=[Depends(require_permission("view", "integrations"))],
)
async def get_log(log_id: int, services: Services) -> IntegrationLogRead:
    log = await IntegrationLogRepository(services.session).get_by_id(log_id)
    if log is None:
        raise NotFoundError("Лог не найден")
    return IntegrationLogRead.model_validate(log)
