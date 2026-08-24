"""Схемы для LPN."""

from __future__ import annotations

from pydantic import BaseModel, Field

from app.api.v1.base_schemas import BaseRead


class LPNRead(BaseRead):
    number: str = Field(..., title="Номер паллета")
    status: str = Field("created", title="Статус")


class LPNCreate(BaseModel):
    status: str = Field("created", title="Статус")
