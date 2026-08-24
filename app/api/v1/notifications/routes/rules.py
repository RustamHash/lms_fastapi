"""API для правил уведомлений."""

from __future__ import annotations

from fastapi import APIRouter, Depends, status

from app.api.deps import Services, require_permission
from app.api.v1.notifications.schemas_rules import (
    NotificationRuleCreate,
    NotificationRuleRead,
    NotificationRuleUpdate,
)
from app.core.exceptions import NotFoundError
from app.notifications.repository import NotificationRuleRepository

router = APIRouter(prefix="/notification-rules", tags=["notification-rules"])


@router.get("", response_model=list[NotificationRuleRead], dependencies=[Depends(require_permission("view", "notifications"))])
async def list_rules(services: Services) -> list[NotificationRuleRead]:
    rows = await NotificationRuleRepository(services.session).list_all()
    return [NotificationRuleRead.model_validate(r) for r in rows]


@router.post("", response_model=NotificationRuleRead, status_code=status.HTTP_201_CREATED, dependencies=[Depends(require_permission("create", "notifications"))])
async def create_rule(body: NotificationRuleCreate, services: Services) -> NotificationRuleRead:
    rule = await NotificationRuleRepository(services.session).create(**body.model_dump())
    return NotificationRuleRead.model_validate(rule)


@router.get("/{rule_id}", response_model=NotificationRuleRead, dependencies=[Depends(require_permission("view", "notifications"))])
async def get_rule(rule_id: int, services: Services) -> NotificationRuleRead:
    rule = await NotificationRuleRepository(services.session).get_by_id(rule_id)
    if rule is None:
        raise NotFoundError("Правило не найдено")
    return NotificationRuleRead.model_validate(rule)


@router.put("/{rule_id}", response_model=NotificationRuleRead, dependencies=[Depends(require_permission("update", "notifications"))])
async def update_rule(rule_id: int, body: NotificationRuleUpdate, services: Services) -> NotificationRuleRead:
    rule = await NotificationRuleRepository(services.session).update(rule_id, **body.model_dump(exclude_unset=True))
    if rule is None:
        raise NotFoundError("Правило не найдено")
    return NotificationRuleRead.model_validate(rule)


@router.delete("/{rule_id}", status_code=status.HTTP_204_NO_CONTENT, dependencies=[Depends(require_permission("delete", "notifications"))])
async def delete_rule(rule_id: int, services: Services) -> None:
    ok = await NotificationRuleRepository(services.session).soft_delete(rule_id)
    if not ok:
        raise NotFoundError("Правило не найдено")
