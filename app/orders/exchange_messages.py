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
    """Заявка на приёмку от партнёра (PORDER после перевода адаптером).

    Поставщик обязателен: в XML `VENDOR/ID` и `VENDOR/NAME`.
    Код склада обязателен: `LOC`. Номер заказа в PORDER сейчас нет — поле пустое.
    """

    number: str
    document_date: date | None
    delivery_date: date | None
    loc_code: str
    vendor: ExchangeVendor
    products: tuple[ExchangeProduct, ...]
    lines: tuple[ExchangeLine, ...]
    order_number: str = ""


@dataclass(frozen=True)
class ExchangeCustomer:
    """Клиент из ORDER/CUSTOMER."""

    code: str
    name: str
    legal_name: str = ""
    inn: str = ""
    kpp: str = ""
    is_edo: bool = False


@dataclass(frozen=True)
class OutboundExchangeMessage:
    """Заявка на отгрузку от партнёра (ORDER после перевода адаптером).

    Обязательны: DOC_NO, LOC, CUSTOMER (ID+NAME), DELIV_ADDR, LN.
    Товары только по существующему справочнику (ITEMS/SUM/COLLECT игнорируются).
    """

    number: str
    document_date: date | None
    delivery_date: date | None
    loc_code: str
    customer: ExchangeCustomer
    delivery_address_raw: str
    needs_delivery: bool
    lines: tuple[ExchangeLine, ...]
    consignee_name: str = ""
    delivery_contact: str = ""
    address_comment: str = ""
