"""API для аудита."""

from __future__ import annotations

from fastapi import APIRouter, Depends

from app.accounts.repository import AuditRepository
from app.accounts.services import AuditService
from app.api.deps import Services, UserDep, require_permission
from app.api.v1.accounts.schemas import AuditCreate, AuditRead

router = APIRouter(tags=["audit"])


@router.get("/audit", response_model=list[AuditRead], dependencies=[Depends(require_permission("view", "audit"))])
async def list_audit(services: Services, user_id: int | None = None) -> list[AuditRead]:
    service = AuditService(AuditRepository(services.session))
    if user_id:
        rows = await service.list_by_user(user_id)
    else:
        rows = await service.list_all()
    return [AuditRead.model_validate(r) for r in rows]


@router.post("/audit", response_model=AuditRead, status_code=201, dependencies=[Depends(require_permission("create", "audit"))])
async def create_audit(body: AuditCreate, services: Services, user_id: UserDep) -> AuditRead:
    service = AuditService(AuditRepository(services.session))
    audit = await service.log(user_id=user_id, action=body.action, entity_type=body.entity_type, entity_id=body.entity_id, changes=body.changes)
    return AuditRead.model_validate(audit)
