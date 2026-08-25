"""Сообщения обмена, которые принимает домен заказов. Без XML."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from decimal import Decimal


@dataclass(frozen=True)
class ExchangeVendor:
    code: str
    name: str
    legal_name: str = ""
    inn: str = ""
    kpp: str = ""


@dataclass(frozen=True)
class ExchangeProduct:
    external_id: str
    name: str
    legal_name: str = ""
    net_mass: Decimal = Decimal("0")
    gross_mass: Decimal = Decimal("0")
    unit: str = ""
    barcode: str = ""
    shelf_life_days: int | None = None
    min_shelf_life_days: int | None = None


@dataclass(frozen=True)
class ExchangeLine:
    external_id: str
    quantity: Decimal
    unit: str = ""


@dataclass(frozen=True)
class InboundExchangeMessage:
    """Заявка на приёмку от партнёра (PORDER после перевода адаптером)."""

    number: str
    document_date: date | None
    delivery_date: date | None
    loc_code: str
    vendor: ExchangeVendor | None
    products: tuple[ExchangeProduct, ...]
    lines: tuple[ExchangeLine, ...]
