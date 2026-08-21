"""Схемы для правил уведомлений."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class NotificationRuleRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    event_type: str
    channel: str
    recipient_type: str
    recipient_id: int | None = None
    role_code: str | None = None
    is_active: bool = True


class NotificationRuleCreate(BaseModel):
    event_type: str = Field(min_length=1, max_length=100)
    channel: str = Field(pattern="^(app|email)$")
    recipient_type: str = Field(pattern="^(user|role)$")
    recipient_id: int | None = None
    role_code: str | None = None
    is_active: bool = True


class NotificationRuleUpdate(BaseModel):
    event_type: str | None = None
    channel: str | None = None
    recipient_type: str | None = None
    recipient_id: int | None = None
    role_code: str | None = None
    is_active: bool | None = None
