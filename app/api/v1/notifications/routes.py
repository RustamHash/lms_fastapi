"""API для модуля notifications."""

from __future__ import annotations

from pydantic import BaseModel
from fastapi import HTTPException, APIRouter, Depends, status

from app.api.deps import SessionDep, UserDep, require_permission
from app.api.v1.notifications import schemas
from app.core.exceptions import NotFoundError, UnauthorizedError
from app.notifications.services import NotificationService
from app.notifications.repository import NotificationRepository

class NotificationUpdate(BaseModel):
    title: str | None = None
    text: str | None = None
    notification_type: str | None = None
    status: str | None = None
    link: str | None = None


router = APIRouter(prefix="/notifications", tags=["notifications"])


@router.get("", response_model=list[schemas.NotificationRead], dependencies=[Depends(require_permission("view", "notifications"))])
async def list_notifications(
    session: SessionDep,
    user_id: UserDep,
) -> list[schemas.NotificationRead]:
    if user_id is None:
        raise UnauthorizedError("Не авторизован")
    service = NotificationService(NotificationRepository(session))
    rows = await service.list_by_user(user_id)
    return [schemas.NotificationRead.model_validate(r) for r in rows]


@router.get("/unread", response_model=list[schemas.NotificationRead], dependencies=[Depends(require_permission("view", "notifications"))])
async def unread_notifications(
    session: SessionDep,
    user_id: UserDep,
) -> list[schemas.NotificationRead]:
    if user_id is None:
        raise UnauthorizedError("Не авторизован")
    service = NotificationService(NotificationRepository(session))
    rows = await service.get_unread(user_id)
    return [schemas.NotificationRead.model_validate(r) for r in rows]


@router.post("", response_model=schemas.NotificationRead, status_code=status.HTTP_201_CREATED, dependencies=[Depends(require_permission("create", "notifications"))])
async def create_notification(
    body: schemas.NotificationCreate,
    session: SessionDep,
) -> schemas.NotificationRead:
    service = NotificationService(NotificationRepository(session))
    notification = await service.create(
        user_id=body.user_id,
        title=body.title,
        text=body.text,
        notification_type=body.notification_type,
        link=body.link,
    )
    return schemas.NotificationRead.model_validate(notification)


@router.patch(
    "/{notification_id}",
    response_model=schemas.NotificationRead,
    dependencies=[Depends(require_permission("update", "notifications"))],
)
async def update_notification(
    notification_id: int,
    body: NotificationUpdate,
    session: SessionDep,
    user_id: UserDep,
) -> schemas.NotificationRead:
    """Обновить уведомление."""
    notification = await NotificationRepository(session).get_by_id(notification_id)
    if notification is None:
        raise NotFoundError("Уведомление не найдено")
    for field in ["title", "text", "notification_type", "status", "link"]:
        for field, value in body.model_dump(exclude_unset=True).items():
            setattr(notification, field, value)
    notification.updated_by_id = user_id
    try:
        await session.flush()
    except Exception as e:
        await session.rollback()
        raise HTTPException(status_code=500, detail=f"Ошибка базы данных: {e}")
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
    notification = await NotificationRepository(session).get_by_id(notification_id)
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
    notification = await NotificationRepository(session).get_by_id(notification_id)
    if notification is None:
        raise NotFoundError("Уведомление не найдено")
    notification.soft_delete(user_id)
    try:
        await session.flush()
    except Exception as e:
        await session.rollback()
        raise HTTPException(status_code=500, detail=f"Ошибка базы данных: {e}")


@router.post("/{notification_id}/read", response_model=schemas.NotificationRead, dependencies=[Depends(require_permission("update", "notifications"))])
async def mark_read(
    notification_id: int,
    session: SessionDep,
) -> schemas.NotificationRead:
    service = NotificationService(NotificationRepository(session))
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
    service = NotificationService(NotificationRepository(session))
    count = await service.mark_all_read(user_id)
    return {"marked": count}
