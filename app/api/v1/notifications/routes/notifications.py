"""API для уведомлений."""

from __future__ import annotations

from fastapi import APIRouter, Depends, status

from app.api.deps import Services, UserDep, require_permission
from app.api.v1.notifications.schemas import NotificationCreate, NotificationRead, NotificationUpdate
from app.core.exceptions import NotFoundError, UnauthorizedError
from app.notifications.repository import NotificationRepository
from app.notifications.services import NotificationService

router = APIRouter(prefix="/notifications", tags=["notifications"])


@router.get("", response_model=list[NotificationRead], dependencies=[Depends(require_permission("view", "notifications"))])
async def list_notifications(services: Services, user_id: UserDep) -> list[NotificationRead]:
    if user_id is None:
        raise UnauthorizedError("Не авторизован")
    rows = await NotificationRepository(services.session).list_by_user(user_id)
    return [NotificationRead.model_validate(r) for r in rows]


@router.get("/unread", response_model=list[NotificationRead], dependencies=[Depends(require_permission("view", "notifications"))])
async def unread_notifications(services: Services, user_id: UserDep) -> list[NotificationRead]:
    if user_id is None:
        raise UnauthorizedError("Не авторизован")
    rows = await NotificationRepository(services.session).list_unread(user_id)
    return [NotificationRead.model_validate(r) for r in rows]


@router.post("", response_model=NotificationRead, status_code=status.HTTP_201_CREATED, dependencies=[Depends(require_permission("create", "notifications"))])
async def create_notification(body: NotificationCreate, services: Services) -> NotificationRead:
    service = NotificationService(NotificationRepository(services.session))
    notification = await service.create(
        user_id=body.user_id,
        title=body.title,
        text=body.text,
        notification_type=body.notification_type,
        link=body.link,
    )
    return NotificationRead.model_validate(notification)


@router.get("/{notification_id}", response_model=NotificationRead, dependencies=[Depends(require_permission("view", "notifications"))])
async def get_notification(notification_id: int, services: Services) -> NotificationRead:
    notification = await NotificationRepository(services.session).get_by_id(notification_id)
    if notification is None:
        raise NotFoundError("Уведомление не найдено")
    return NotificationRead.model_validate(notification)


@router.patch("/{notification_id}", response_model=NotificationRead, dependencies=[Depends(require_permission("update", "notifications"))])
async def update_notification(notification_id: int, body: NotificationUpdate, services: Services, user_id: UserDep) -> NotificationRead:
    notification = await NotificationRepository(services.session).update(notification_id, **body.model_dump(exclude_unset=True))
    if notification is None:
        raise NotFoundError("Уведомление не найдено")
    return NotificationRead.model_validate(notification)


@router.delete("/{notification_id}", status_code=status.HTTP_204_NO_CONTENT, dependencies=[Depends(require_permission("delete", "notifications"))])
async def delete_notification(notification_id: int, services: Services, user_id: UserDep) -> None:
    ok = await NotificationRepository(services.session).soft_delete(notification_id, user_id)
    if not ok:
        raise NotFoundError("Уведомление не найдено")


@router.post("/{notification_id}/read", response_model=NotificationRead, dependencies=[Depends(require_permission("update", "notifications"))])
async def mark_read(notification_id: int, services: Services) -> NotificationRead:
    service = NotificationService(NotificationRepository(services.session))
    notification = await service.mark_read(notification_id)
    if notification is None:
        raise NotFoundError("Уведомление не найдено")
    return NotificationRead.model_validate(notification)


@router.post("/mark-all-read")
async def mark_all_read(services: Services, user_id: UserDep) -> dict[str, int]:
    if user_id is None:
        raise UnauthorizedError("Не авторизован")
    service = NotificationService(NotificationRepository(services.session))
    count = await service.mark_all_read(user_id)
    return {"marked": count}
