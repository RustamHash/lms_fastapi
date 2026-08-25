"""Адаптер для поклажедателя Зиландия (ZLN)."""

from __future__ import annotations

import asyncio
import xml.etree.ElementTree as ET
from datetime import datetime
from decimal import Decimal

from app.integration.adapters.base import BaseAdapter
from app.orders.exchange_messages import (
    ExchangeLine,
    ExchangeProduct,
    ExchangeVendor,
    InboundExchangeMessage,
)


class ZLNAdapter(BaseAdapter):
    """Парсинг XML-файлов Зиландии."""

    async def parse(self, file_path: str):
        """Асинхронный парсинг XML через executor."""
        loop = asyncio.get_event_loop()
        tree = await loop.run_in_executor(None, ET.parse, file_path)
        root = tree.getroot()

        if root.tag == "PORDER":
            return self._parse_porder(root)
        elif root.tag == "ORDER":
            return self._parse_order(root)
        else:
            return None, [f"Неизвестный тип документа: {root.tag}"]

    @staticmethod
    def _optional_text(element, tag: str) -> str:
        child = element.find(tag)
        return child.text.strip() if child is not None and child.text else ""

    def _require_text(self, element, tag: str, errors: list[str], where: str) -> str:
        value = self._optional_text(element, tag)
        if not value:
            errors.append(f"{where}: нет тега {tag}")
        return value

    @staticmethod
    def _parse_date(text):
        if not text:
            return None
        try:
            return datetime.strptime(text, "%Y%m%d").date()
        except ValueError:
            return None

    @staticmethod
    def _parse_decimal(text):
        if not text:
            return Decimal("0")
        try:
            return Decimal(text.replace(",", "."))
        except Exception:
            return Decimal("0")

    @staticmethod
    def _parse_int(text):
        if not text:
            return None
        try:
            return int(text.strip())
        except ValueError:
            return None

    def _parse_vendor(self, root, errors: list[str], doc_no: str) -> ExchangeVendor | None:
        where = f"{doc_no or 'PORDER'}: VENDOR"
        vendor_el = root.find("VENDOR")
        if vendor_el is None:
            errors.append(f"{where}: нет блока VENDOR")
            return None
        vendor_id = self._require_text(vendor_el, "ID", errors, where)
        vendor_name = self._require_text(vendor_el, "NAME", errors, where)
        if not vendor_id or not vendor_name:
            return None
        return ExchangeVendor(
            code=vendor_id,
            name=vendor_name,
            legal_name=self._optional_text(vendor_el, "LEGAL_NAME"),
            inn=self._optional_text(vendor_el, "INN"),
            kpp=self._optional_text(vendor_el, "KPP"),
        )

    def _parse_items(self, root, errors: list[str], doc_no: str) -> list[ExchangeProduct]:
        items: list[ExchangeProduct] = []
        items_el = root.find("ITEMS")
        item_els = list(items_el.findall("ITEM")) if items_el is not None else []
        if not item_els:
            errors.append(f"{doc_no}: Нет товаров в документе")
            return items

        for item_el in item_els:
            where = f"{doc_no}: ITEM"
            item_id = self._require_text(item_el, "ID", errors, where)
            name = self._require_text(item_el, "NAME", errors, f"{where} {item_id or ''}".rstrip())
            if not item_id or not name:
                continue
            items.append(
                ExchangeProduct(
                    external_id=item_id,
                    name=name,
                    legal_name=self._optional_text(item_el, "LEGAL_NAME"),
                    unit=self._optional_text(item_el, "BUM"),
                    barcode=self._optional_text(item_el, "EAN"),
                    gross_mass=self._parse_decimal(self._optional_text(item_el, "GROSS_MASS")),
                    net_mass=self._parse_decimal(self._optional_text(item_el, "NET_MASS")),
                    shelf_life_days=self._parse_int(self._optional_text(item_el, "TOTALSHELFLIFE")),
                    min_shelf_life_days=self._parse_int(self._optional_text(item_el, "MINSHELFLIFE")),
                )
            )
        return items

    def _parse_lines(self, root, errors: list[str], doc_no: str) -> list[ExchangeLine]:
        lines: list[ExchangeLine] = []
        ln_els = root.findall("LN")
        if not ln_els:
            errors.append(f"{doc_no}: Нет строк в документе")
            return lines

        for ln_el in ln_els:
            where = f"{doc_no}: LN"
            item_id = self._require_text(ln_el, "ITEM", errors, where)
            quantity = self._require_text(ln_el, "QNT", errors, where)
            if not item_id or not quantity:
                continue
            try:
                qty = int(quantity)
            except ValueError:
                errors.append(f"{where}: QNT не число")
                continue
            if qty <= 0:
                errors.append(f"{where}: QNT должно быть больше 0")
                continue
            lines.append(
                ExchangeLine(
                    external_id=item_id,
                    quantity=Decimal(qty),
                    unit=self._optional_text(ln_el, "UNIT"),
                )
            )
        return lines

    def _parse_porder(self, root):
        """Парсинг входящего заказа (PORDER)."""
        errors: list[str] = []

        doc_no = self._require_text(root, "DOC_NO", errors, "PORDER")
        loc = self._require_text(root, "LOC", errors, "PORDER")
        doc_date = self._parse_date(self._optional_text(root, "DOC_DATE"))
        delivery_date = self._parse_date(self._optional_text(root, "DELIV_DATE"))

        vendor = self._parse_vendor(root, errors, doc_no)
        items = self._parse_items(root, errors, doc_no or "PORDER")
        lines = self._parse_lines(root, errors, doc_no or "PORDER")

        if errors or vendor is None:
            return None, errors

        return InboundExchangeMessage(
            number=doc_no,
            document_date=doc_date,
            delivery_date=delivery_date,
            loc_code=loc,
            vendor=vendor,
            products=tuple(items),
            lines=tuple(lines),
        ), []

    def _parse_order(self, root):
        """Исходящий ORDER — не этот контур."""
        doc_no = self._optional_text(root, "DOC_NO") or "ORDER"
        return None, [
            f"{doc_no}: исходящий ORDER пока не принимается с обмена"
        ]
