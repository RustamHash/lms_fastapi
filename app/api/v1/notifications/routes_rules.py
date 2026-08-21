"""API для управления правилами уведомлений."""

from __future__ import annotations

from fastapi import APIRouter, Depends, status
from sqlalchemy import select

from app.api.deps import SessionDep, UserDep, require_permission
from app.api.v1.notifications.schemas_rules import (
    NotificationRuleCreate,
    NotificationRuleRead,
    NotificationRuleUpdate,
)
from app.core.exceptions import NotFoundError
from app.notifications.repository import NotificationRuleRepository
from app.notifications.models import NotificationRule

router = APIRouter(prefix="/notification-rules", tags=["notification-rules"])


@router.get(
    "",
    response_model=list[NotificationRuleRead],
    dependencies=[Depends(require_permission("view", "notifications"))],
)
async def list_rules(session: SessionDep) -> list[NotificationRuleRead]:
    """Список правил."""
    rules = await NotificationRuleRepository(session).list_all()
    return [NotificationRuleRead.model_validate(r) for r in rules]


@router.post(
    "",
    response_model=NotificationRuleRead,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_permission("create", "notifications"))],
)
async def create_rule(
    body: NotificationRuleCreate,
    session: SessionDep,
) -> NotificationRuleRead:
    """Создать правило."""
    rule = NotificationRule(**body.model_dump())
    session.add(rule)
    await session.flush()
    return NotificationRuleRead.model_validate(rule)


@router.get(
    "/{rule_id}",
    response_model=NotificationRuleRead,
    dependencies=[Depends(require_permission("view", "notifications"))],
)
async def get_rule(rule_id: int, session: SessionDep) -> NotificationRuleRead:
    rule = await NotificationRuleRepository(session).get_by_id(rule_id)
    if rule is None:
        raise NotFoundError("Правило не найдено")
    return NotificationRuleRead.model_validate(rule)


@router.put(
    "/{rule_id}",
    response_model=NotificationRuleRead,
    dependencies=[Depends(require_permission("update", "notifications"))],
)
async def update_rule(
    rule_id: int,
    body: NotificationRuleUpdate,
    session: SessionDep,
) -> NotificationRuleRead:
    """Обновить правило."""
    rule = await NotificationRuleRepository(session).get_by_id(rule_id)
    if rule is None:
        raise NotFoundError("Правило не найдено")
    for field, value in body.model_dump(exclude_unset=True).items():
        setattr(rule, field, value)
    await session.flush()
    return NotificationRuleRead.model_validate(rule)


@router.delete(
    "/{rule_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(require_permission("delete", "notifications"))],
)
async def delete_rule(rule_id: int, session: SessionDep) -> None:
    """Удалить правило."""
    rule = await NotificationRuleRepository(session).get_by_id(rule_id)
    if rule is None:
        raise NotFoundError("Правило не найдено")
    await session.delete(rule)
    await session.flush()
