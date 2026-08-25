"""Парсер ZLN ORDER — без БД."""

from __future__ import annotations

from datetime import date
from decimal import Decimal
from xml.etree.ElementTree import fromstring

from app.integration.adapters.zln_adapter import ZLNAdapter
from app.orders.exchange_messages import OutboundExchangeMessage

ORDER_XML = """
<ORDER>
  <PARTNER>ZLN</PARTNER>
  <DOC_NO>10000221735</DOC_NO>
  <DOC_DATE>20260817</DOC_DATE>
  <CUSTOMER>
    <ID>Z000004338</ID>
    <NAME>ИП Железняк</NAME>
    <LEGAL_NAME>ИП Железняк Александр Владимирович</LEGAL_NAME>
    <INN>615424242005</INN>
    <KPP/>
    <USE_EDO>0</USE_EDO>
  </CUSTOMER>
  <DELIV_DATE>20260818</DELIV_DATE>
  <LOC>0000001</LOC>
  <COLLECT>0</COLLECT>
  <SUM>112806,95</SUM>
  <DELIV>1</DELIV>
  <CONSIG>ИП Железняк Александр Владимирович</CONSIG>
  <CONSIG_CONT>Александр +7 (919) 8899849</CONSIG_CONT>
  <DELIV_ADDR>
347923, Ростовская обл, Таганрог г, Инструментальная ул, дом 23
  </DELIV_ADDR>
  <ITEMS>
    <ITEM>
      <ID>700009616</ID>
      <NAME>ПОМАДКА</NAME>
    </ITEM>
  </ITEMS>
  <LN>
    <ITEM>700009616</ITEM>
    <UNIT>шт</UNIT>
    <QNT>13</QNT>
  </LN>
  <LN>
    <ITEM>700004010</ITEM>
    <UNIT>шт</UNIT>
    <QNT>8</QNT>
  </LN>
</ORDER>
"""


def test_parse_order_fields() -> None:
    doc, errors = ZLNAdapter()._parse_order(fromstring(ORDER_XML))
    assert errors == []
    assert isinstance(doc, OutboundExchangeMessage)
    assert doc.number == "10000221735"
    assert doc.document_date == date(2026, 8, 17)
    assert doc.delivery_date == date(2026, 8, 18)
    assert doc.loc_code == "0000001"
    assert doc.needs_delivery is True
    assert doc.customer.code == "Z000004338"
    assert doc.customer.name == "ИП Железняк"
    assert "Инструментальная" in doc.delivery_address_raw
    assert doc.consignee_name.startswith("ИП Железняк")
    assert "919" in doc.delivery_contact
    assert len(doc.lines) == 2
    assert doc.lines[0].external_id == "700009616"
    assert doc.lines[0].quantity == Decimal("13")


def test_parse_order_deliv_zero_is_pickup() -> None:
    xml = ORDER_XML.replace("<DELIV>1</DELIV>", "<DELIV>0</DELIV>")
    doc, errors = ZLNAdapter()._parse_order(fromstring(xml))
    assert errors == []
    assert doc is not None
    assert doc.needs_delivery is False


def test_parse_order_without_deliv_addr_is_error() -> None:
    xml = """
    <ORDER>
      <DOC_NO>O-1</DOC_NO>
      <LOC>0001</LOC>
      <CUSTOMER>
        <ID>C1</ID>
        <NAME>Клиент</NAME>
      </CUSTOMER>
      <DELIV>0</DELIV>
      <LN><ITEM>SKU1</ITEM><QNT>1</QNT></LN>
    </ORDER>
    """
    doc, errors = ZLNAdapter()._parse_order(fromstring(xml))
    assert doc is None
    assert any("DELIV_ADDR" in e for e in errors)


def test_parse_order_without_customer_is_error() -> None:
    xml = """
    <ORDER>
      <DOC_NO>O-2</DOC_NO>
      <LOC>0001</LOC>
      <DELIV_ADDR>г. Москва</DELIV_ADDR>
      <LN><ITEM>SKU1</ITEM><QNT>1</QNT></LN>
    </ORDER>
    """
    doc, errors = ZLNAdapter()._parse_order(fromstring(xml))
    assert doc is None
    assert any("CUSTOMER" in e for e in errors)


def test_parse_order_without_lines_is_error() -> None:
    xml = """
    <ORDER>
      <DOC_NO>O-3</DOC_NO>
      <LOC>0001</LOC>
      <CUSTOMER>
        <ID>C1</ID>
        <NAME>Клиент</NAME>
      </CUSTOMER>
      <DELIV_ADDR>г. Москва</DELIV_ADDR>
    </ORDER>
    """
    doc, errors = ZLNAdapter()._parse_order(fromstring(xml))
    assert doc is None
    assert any("Нет строк" in e for e in errors)
