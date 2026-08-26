"""Генерация ответного XML Зиландии."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime
from decimal import Decimal
from xml.etree.ElementTree import Element, SubElement, tostring
from zoneinfo import ZoneInfo

MOSCOW = ZoneInfo("Europe/Moscow")


def _ymd(value: date | None) -> str:
    if value is None:
        return ""
    return value.strftime("%Y%m%d")


def _now_stamp() -> str:
    return datetime.now(MOSCOW).strftime("%Y%m%d-%H%M%S")


def _xml_bytes(root: Element) -> bytes:
    return tostring(root, encoding="utf-8", xml_declaration=True)


@dataclass(frozen=True)
class ExportLine:
    item: str
    lot: str
    date_exp: date | None
    unit: str
    quantity: Decimal


def build_pordrsp(
    *,
    partner: str,
    doc_no: str,
    order_date: date | None,
) -> tuple[str, bytes]:
    """Подтверждение принятия PORDER. Даты — дата заказа."""
    root = Element("PORDRSP")
    SubElement(root, "PARTNER").text = partner
    SubElement(root, "DOC_NO").text = doc_no
    SubElement(root, "DOC_DATE").text = _ymd(order_date)
    SubElement(root, "ORD_NO").text = doc_no
    SubElement(root, "ORD_DATE").text = _ymd(order_date)
    name = f"pordrsp_{doc_no}_{_now_stamp()}.xml"
    return name, _xml_bytes(root)


def build_ordrsp(
    *,
    partner: str,
    doc_no: str,
    order_date: date | None,
) -> tuple[str, bytes]:
    """Подтверждение принятия ORDER."""
    root = Element("ORDRSP")
    SubElement(root, "PARTNER").text = partner
    SubElement(root, "DOC_NO").text = doc_no
    SubElement(root, "DOC_DATE").text = _ymd(order_date)
    SubElement(root, "ORD_NO").text = doc_no
    SubElement(root, "ORD_DATE").text = _ymd(order_date)
    name = f"ordrsp_{doc_no}_{_now_stamp()}.xml"
    return name, _xml_bytes(root)


def build_recadv(
    *,
    partner: str,
    doc_no: str,
    order_date: date | None,
    lines: list[ExportLine],
) -> tuple[str, bytes]:
    """Факт приёмки после задания."""
    root = Element("RECADV")
    SubElement(root, "PARTNER").text = partner
    SubElement(root, "DOC_NO").text = doc_no
    SubElement(root, "DOC_DATE").text = _ymd(order_date)
    SubElement(root, "ORD_NO").text = doc_no
    SubElement(root, "ORD_DATE").text = _ymd(order_date)
    for line in lines:
        ln = SubElement(root, "LN")
        SubElement(ln, "ITEM").text = line.item
        SubElement(ln, "LOT").text = line.lot
        SubElement(ln, "DATE_EXP").text = _ymd(line.date_exp)
        SubElement(ln, "UNIT").text = line.unit or "шт"
        SubElement(ln, "QNT").text = str(int(line.quantity))
    name = f"recadv_{doc_no}_{_now_stamp()}.xml"
    return name, _xml_bytes(root)


def build_desadv(
    *,
    partner: str,
    doc_no: str,
    order_date: date | None,
    lines: list[ExportLine],
) -> tuple[str, bytes]:
    """Факт отгрузки после отбора. Теги ORDER_NO / ORDER_DATE — как у партнёра."""
    root = Element("DESADV")
    SubElement(root, "PARTNER").text = partner
    SubElement(root, "DOC_NO").text = doc_no
    SubElement(root, "DOC_DATE").text = _ymd(order_date)
    SubElement(root, "ORDER_NO").text = doc_no
    SubElement(root, "ORDER_DATE").text = _ymd(order_date)
    for line in lines:
        ln = SubElement(root, "LN")
        SubElement(ln, "ITEM").text = line.item
        SubElement(ln, "LOT").text = line.lot
        SubElement(ln, "DATE_EXP").text = _ymd(line.date_exp)
        SubElement(ln, "UNIT").text = line.unit or "шт"
        SubElement(ln, "QNT").text = str(int(line.quantity))
    name = f"desadv_{doc_no}_{_now_stamp()}.xml"
    return name, _xml_bytes(root)
