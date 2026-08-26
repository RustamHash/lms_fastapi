"""Генерация ответного XML ZLN — без БД."""

from __future__ import annotations

from datetime import date
from decimal import Decimal
from xml.etree.ElementTree import fromstring

from app.integration.exporters.zln_xml import (
    ExportLine,
    build_desadv,
    build_ordrsp,
    build_pordrsp,
    build_recadv,
)


def test_pordrsp_uses_order_date_and_tags():
    name, body = build_pordrsp(
        partner="ZLN",
        doc_no="10000221735",
        order_date=date(2026, 8, 17),
    )
    assert name.startswith("pordrsp_10000221735_")
    assert name.endswith(".xml")
    root = fromstring(body)
    assert root.tag == "PORDRSP"
    assert root.findtext("PARTNER") == "ZLN"
    assert root.findtext("DOC_NO") == "10000221735"
    assert root.findtext("DOC_DATE") == "20260817"
    assert root.findtext("ORD_NO") == "10000221735"
    assert root.findtext("ORD_DATE") == "20260817"
    assert root.find("LN") is None


def test_ordrsp_root_and_tags():
    name, body = build_ordrsp(
        partner="ZLN",
        doc_no="ORD-1",
        order_date=date(2026, 1, 2),
    )
    root = fromstring(body)
    assert root.tag == "ORDRSP"
    assert name.startswith("ordrsp_ORD-1_")
    assert root.findtext("ORD_NO") == "ORD-1"


def test_recadv_lines():
    name, body = build_recadv(
        partner="ZLN",
        doc_no="P-1",
        order_date=date(2026, 3, 4),
        lines=[
            ExportLine(
                item="700009616",
                lot="L1",
                date_exp=date(2027, 1, 15),
                unit="шт",
                quantity=Decimal("10"),
            )
        ],
    )
    root = fromstring(body)
    assert root.tag == "RECADV"
    assert name.startswith("recadv_P-1_")
    ln = root.find("LN")
    assert ln is not None
    assert ln.findtext("ITEM") == "700009616"
    assert ln.findtext("LOT") == "L1"
    assert ln.findtext("DATE_EXP") == "20270115"
    assert ln.findtext("QNT") == "10"


def test_desadv_uses_order_no_tags():
    """DESADV у партнёра — ORDER_NO / ORDER_DATE, не ORD_*."""
    _, body = build_desadv(
        partner="ZLN",
        doc_no="O-9",
        order_date=date(2026, 5, 6),
        lines=[],
    )
    root = fromstring(body)
    assert root.tag == "DESADV"
    assert root.findtext("ORDER_NO") == "O-9"
    assert root.findtext("ORDER_DATE") == "20260506"
    assert root.find("ORD_NO") is None
