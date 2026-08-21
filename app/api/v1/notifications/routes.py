"""API для модуля notifications."""

from __future__ import annotations

from fastapi import APIRouter, Depends, status

from app.api.deps import SessionDep, UserDep, require_permission
from app.api.v1.notifications import schemas
from app.core.exceptions import NotFoundError, UnauthorizedError
from app.notifications.services import NotificationService

router = APIRouter(prefix="/notifications", tags=["notifications"])


@router.get("", response_model=list[schemas.NotificationRead], dependencies=[Depends(require_permission("view", "notifications"))])
async def list_notifications(
    session: SessionDep,
    user_id: UserDep,
) -> list[schemas.NotificationRead]:
    if user_id is None:
        raise UnauthorizedError("Не авторизован")
    service = NotificationService(session)
    rows = await service.list_by_user(user_id)
    return [schemas.NotificationRead.model_validate(r) for r in rows]


@router.get("/unread", response_model=list[schemas.NotificationRead], dependencies=[Depends(require_permission("view", "notifications"))])
async def unread_notifications(
    session: SessionDep,
    user_id: UserDep,
) -> list[schemas.NotificationRead]:
    if user_id is None:
        raise UnauthorizedError("Не авторизован")
    service = NotificationService(session)
    rows = await service.get_unread(user_id)
    return [schemas.NotificationRead.model_validate(r) for r in rows]


@router.post("", response_model=schemas.NotificationRead, status_code=status.HTTP_201_CREATED, dependencies=[Depends(require_permission("create", "notifications"))])
async def create_notification(
    body: schemas.NotificationCreate,
    session: SessionDep,
) -> schemas.NotificationRead:
    service = NotificationService(session)
    notification = await service.create(
        user_id=body.user_id,
        title=body.title,
        text=body.text,
        notification_type=body.notification_type,
        link=body.link,
    )
    return schemas.NotificationRead.model_validate(notification)


@router.get(
    "/{notification_id}",
    response_model=schemas.NotificationRead,
    dependencies=[Depends(require_permission("view", "notifications"))],
)
async def get_notification(
    notification_id: int,
    session: SessionDep,
) -> schemas.NotificationRead:
    from app.notifications.models import Notification
    notification = await session.get(Notification, notification_id)
    if notification is None:
        raise NotFoundError("Уведомление не найдено")
    return schemas.NotificationRead.model_validate(notification)


@router.delete(
    "/{notification_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(require_permission("delete", "notifications"))],
)
async def delete_notification(
    notification_id: int,
    session: SessionDep,
    user_id: UserDep,
) -> None:
    from app.notifications.models import Notification
    notification = await session.get(Notification, notification_id)
    if notification is None:
        raise NotFoundError("Уведомление не найдено")
    notification.soft_delete(user_id)
    await session.flush()


@router.post("/{notification_id}/read", response_model=schemas.NotificationRead, dependencies=[Depends(require_permission("update", "notifications"))])
async def mark_read(
    notification_id: int,
    session: SessionDep,
) -> schemas.NotificationRead:
    service = NotificationService(session)
    notification = await service.mark_read(notification_id)
    if notification is None:
        raise NotFoundError("Уведомление не найдено")
    return schemas.NotificationRead.model_validate(notification)


@router.post("/mark-all-read")
async def mark_all_read(
    session: SessionDep,
    user_id: UserDep,
) -> dict:
    if user_id is None:
        raise UnauthorizedError("Не авторизован")
    service = NotificationService(session)
    count = await service.mark_all_read(user_id)
    return {"marked": count}
