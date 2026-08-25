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
    def _get_text(element, tag):
        child = element.find(tag)
        return child.text.strip() if child is not None and child.text else ""

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

    def _parse_items(self, root):
        """Парсинг ITEMS — общий для PORDER и ORDER."""
        items = []
        items_el = root.find("ITEMS")
        if items_el is not None:
            for item_el in items_el.findall("ITEM"):
                item_id = self._get_text(item_el, "ID")
                if not item_id:
                    continue

                shelf_life = self._get_text(item_el, "TOTALSHELFLIFE")
                min_shelf_life = self._get_text(item_el, "MINSHELFLIFE")

                items.append(
                    ExchangeProduct(
                        external_id=item_id,
                        name=self._get_text(item_el, "NAME"),
                        legal_name=self._get_text(item_el, "LEGAL_NAME"),
                        unit=self._get_text(item_el, "BUM"),
                        barcode=self._get_text(item_el, "EAN"),
                        gross_mass=self._parse_decimal(
                            self._get_text(item_el, "GROSS_MASS")
                        ),
                        net_mass=self._parse_decimal(
                            self._get_text(item_el, "NET_MASS")
                        ),
                        shelf_life_days=self._parse_int(shelf_life),
                        min_shelf_life_days=self._parse_int(min_shelf_life),
                    )
                )

        return items

    def _parse_lines(self, root):
        """Парсинг строк (LN) — общий для PORDER и ORDER."""
        lines = []
        for ln_el in root.findall("LN"):
            item_id = self._get_text(ln_el, "ITEM")
            quantity = self._get_text(ln_el, "QNT")

            if not item_id:
                continue

            try:
                qty = int(quantity)
            except ValueError:
                continue

            if qty <= 0:
                continue

            lines.append(
                ExchangeLine(
                    external_id=item_id,
                    quantity=Decimal(qty),
                    unit=self._get_text(ln_el, "UNIT"),
                )
            )

        return lines

    def _parse_porder(self, root):
        """Парсинг входящего заказа (PORDER)."""
        errors = []

        doc_no = self._get_text(root, "DOC_NO")
        doc_date = self._parse_date(self._get_text(root, "DOC_DATE"))
        delivery_date = self._parse_date(self._get_text(root, "DELIV_DATE"))
        loc = self._get_text(root, "LOC")

        # Поставщик (VENDOR)
        vendor_id = self._get_text(root, "VENDOR/ID")
        vendor_name = self._get_text(root, "VENDOR/NAME")
        vendor_legal_name = self._get_text(root, "VENDOR/LEGAL_NAME")
        vendor_inn = self._get_text(root, "VENDOR/INN")
        vendor_kpp = self._get_text(root, "VENDOR/KPP")

        if not doc_no:
            errors.append("Номер документа не указан")

        items = self._parse_items(root)
        lines = self._parse_lines(root)

        if not items:
            errors.append(f"{doc_no}: Нет товаров в документе")
        if not lines:
            errors.append(f"{doc_no}: Нет строк в документе")

        if errors:
            return None, errors

        vendor = None
        if vendor_id:
            vendor = ExchangeVendor(
                code=vendor_id,
                name=vendor_name,
                legal_name=vendor_legal_name,
                inn=vendor_inn,
                kpp=vendor_kpp,
            )

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
        doc_no = self._get_text(root, "DOC_NO") or "ORDER"
        return None, [
            f"{doc_no}: исходящий ORDER пока не принимается с обмена"
        ]
