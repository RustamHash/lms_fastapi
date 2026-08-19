"""Схемы для модуля notifications."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class NotificationRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    title: str
    text: str
    notification_type: str = "system"
    status: str = "pending"
    link: str = ""
    sent_at: str | None = None
    read_at: str | None = None


class NotificationCreate(BaseModel):
    user_id: int
    title: str
    text: str
    notification_type: str = "system"
    link: str = ""
