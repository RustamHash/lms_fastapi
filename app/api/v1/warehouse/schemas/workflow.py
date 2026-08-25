"""Схемы воркфлоу приёмки и отбора."""

from __future__ import annotations

from datetime import date
from decimal import Decimal

from pydantic import BaseModel, Field


class ReceivingFromInbound(BaseModel):
    inbound_order_id: int = Field(..., title="Входящий заказ")
    receiving_location_id: int = Field(..., title="Ячейка приёмки")


class ReceiveLineBody(BaseModel):
    quantity: Decimal = Field(..., title="Количество")
    batch_number: str = Field(..., title="Номер партии")
    location_id: int | None = Field(None, title="Ячейка")
    lpn_id: int | None = Field(None, title="LPN")
    manufacture_date: date | None = Field(None, title="Дата производства")


class ReceivingCompleteBody(BaseModel):
    confirm_shortage: bool = Field(False, title="Подтвердить недогруз")


class PickingFromOutbound(BaseModel):
    outbound_order_id: int = Field(..., title="Исходящий заказ")


class PickLineBody(BaseModel):
    quantity: Decimal = Field(..., title="Количество")
