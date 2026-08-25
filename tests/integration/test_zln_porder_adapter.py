"""Парсер ZLN PORDER — без БД."""

from __future__ import annotations

from datetime import date
from decimal import Decimal
from xml.etree.ElementTree import fromstring

from app.integration.adapters.zln_adapter import ZLNAdapter
from app.orders.exchange_messages import InboundExchangeMessage

PORDER_XML = """
<PORDER>
  <DOC_NO>P-100</DOC_NO>
  <DOC_DATE>20260825</DOC_DATE>
  <DELIV_DATE>20260826</DELIV_DATE>
  <LOC>0001</LOC>
  <PARTNER>ZLN</PARTNER>
  <VENDOR>
    <ID>V1</ID>
    <NAME>Поставщик</NAME>
    <LEGAL_NAME>ООО Поставщик</LEGAL_NAME>
    <INN>1234567890</INN>
    <KPP>123456789</KPP>
  </VENDOR>
  <ITEMS>
    <ITEM>
      <ID>SKU1</ID>
      <NAME>Товар</NAME>
      <NET_MASS>1.5</NET_MASS>
    </ITEM>
  </ITEMS>
  <LN>
    <ITEM>SKU1</ITEM>
    <QNT>10</QNT>
  </LN>
</PORDER>
"""


def test_parse_porder_fields() -> None:
    doc, errors = ZLNAdapter()._parse_porder(fromstring(PORDER_XML))
    assert errors == []
    assert isinstance(doc, InboundExchangeMessage)
    assert doc.number == "P-100"
    assert doc.document_date == date(2026, 8, 25)
    assert doc.delivery_date == date(2026, 8, 26)
    assert doc.loc_code == "0001"
    assert doc.vendor is not None
    assert doc.vendor.code == "V1"
    assert doc.products[0].external_id == "SKU1"
    assert doc.products[0].net_mass == Decimal("1.5")
    assert doc.lines[0].external_id == "SKU1"
    assert doc.lines[0].quantity == Decimal("10")


def test_parse_porder_without_lines_is_error() -> None:
    xml = """
    <PORDER>
      <DOC_NO>P-2</DOC_NO>
      <ITEMS>
        <ITEM><ID>SKU1</ID><NAME>Товар</NAME></ITEM>
      </ITEMS>
    </PORDER>
    """
    doc, errors = ZLNAdapter()._parse_porder(fromstring(xml))
    assert doc is None
    assert any("Нет строк" in e for e in errors)
