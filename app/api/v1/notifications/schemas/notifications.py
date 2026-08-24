"""Схемы для уведомлений."""

from __future__ import annotations

from pydantic import BaseModel, Field

from app.api.v1.base_schemas import BaseRead


class NotificationRead(BaseRead):
    user_id: int = Field(..., title="Получатель")
    title: str = Field(..., title="Заголовок")
    text: str = Field(..., title="Текст")
    notification_type: str = Field("system", title="Тип уведомления")
    status: str = Field("pending", title="Статус")
    link: str = Field("", title="Ссылка")
    sent_at: str | None = Field(None, title="Когда отправлено")
    read_at: str | None = Field(None, title="Когда прочитано")


class NotificationCreate(BaseModel):
    user_id: int = Field(..., title="Получатель")
    title: str = Field(..., title="Заголовок")
    text: str = Field(..., title="Текст")
    notification_type: str = Field("system", title="Тип уведомления")
    link: str = Field("", title="Ссылка")


class NotificationUpdate(BaseModel):
    title: str | None = Field(None, title="Заголовок")
    text: str | None = Field(None, title="Текст")
    notification_type: str | None = Field(None, title="Тип уведомления")
    status: str | None = Field(None, title="Статус")
    link: str | None = Field(None, title="Ссылка")
