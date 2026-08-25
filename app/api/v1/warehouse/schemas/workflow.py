"""Схемы воркфлоу приёмки и отбора."""

from __future__ import annotations

from datetime import date, datetime
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


class PlanFactLineRead(BaseModel):
    id: int
    product_id: int | None = None
    product_sku: str = ""
    product_name: str = ""
    quantity: Decimal
    batch_number: str = ""
    manufacture_date: date | None = None


class PlanFactMovementRead(BaseModel):
    id: int
    moved_at: datetime
    direction: str
    quantity: Decimal
    product_id: int
    product_sku: str = ""
    product_name: str = ""
    batch_number: str = ""
    lpn_number: str = ""
    location_id: int
    task_line_id: int | None = None
    production_date: date | None = None
    expiration_date: date | None = None
    remaining_days: int | None = None
    remaining_percent: Decimal | None = None


class PlanFactDiscrepancyRead(BaseModel):
    inbound_order_line_id: int | None = None
    product_id: int | None = None
    product_sku: str = ""
    product_name: str = ""
    qty_planned: Decimal
    qty_fact: Decimal
    qty_diff: Decimal
    kind: str


class PlanFactRead(BaseModel):
    plan: list[PlanFactLineRead]
    fact: list[PlanFactMovementRead]
    discrepancies: list[PlanFactDiscrepancyRead]


InboundPlanLineRead = PlanFactLineRead
InboundFactMovementRead = PlanFactMovementRead
InboundDiscrepancyRead = PlanFactDiscrepancyRead
InboundPlanFactRead = PlanFactRead
