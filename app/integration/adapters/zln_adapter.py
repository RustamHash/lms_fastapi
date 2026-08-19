"""Адаптер для поклажедателя Зиландия (ZLN)."""

from __future__ import annotations

import xml.etree.ElementTree as ET
from datetime import datetime
from decimal import Decimal

from app.integration.adapters.base import BaseAdapter


class ZLNAdapter(BaseAdapter):
    """Парсинг XML-файлов Зиландии."""

    def parse(self, file_path: str):
        tree = ET.parse(file_path)
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
        return child.text or "" if child is not None else ""

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

    def _parse_porder(self, root):
        errors = []

        partner = self._get_text(root, "PARTNER")
        doc_no = self._get_text(root, "DOC_NO")
        doc_date = self._parse_date(self._get_text(root, "DOC_DATE"))
        delivery_date = self._parse_date(self._get_text(root, "DELIV_DATE"))
        loc = self._get_text(root, "LOC")

        if not partner:
            errors.append("PARTNER не указан")
        if not doc_no:
            errors.append("Номер документа не указан")

        items = []
        items_el = root.find("ITEMS")
        if items_el is not None:
            for item_el in items_el.findall("ITEM"):
                item_id = self._get_text(item_el, "ID")
                name = self._get_text(item_el, "NAME")
                ean = self._get_text(item_el, "EAN")
                weight = self._parse_decimal(self._get_text(item_el, "NET_MASS"))
                shelf_life = self._get_text(item_el, "TOTALSHELFLIFE")

                if not item_id:
                    errors.append(f"{doc_no}: ID товара не указан")
                    continue

                items.append({
                    "external_id": item_id,
                    "name": name,
                    "ean": ean,
                    "weight": weight,
                    "shelf_life_days": int(shelf_life) if shelf_life.isdigit() else None,
                })

        lines = []
        for ln_el in root.findall("LN"):
            item_id = self._get_text(ln_el, "ITEM")
            quantity = self._get_text(ln_el, "QNT")

            if not item_id:
                errors.append(f"{doc_no}: Товар не указан в строке")
                continue

            try:
                qty = int(quantity)
            except ValueError:
                errors.append(f"{doc_no}: Некорректное количество {quantity}")
                continue

            if qty <= 0:
                errors.append(f"{doc_no}: Количество должно быть больше 0")
                continue

            lines.append({
                "external_id": item_id,
                "quantity": qty,
            })

        if errors:
            return None, errors

        return {
            "document_type": "porder",
            "document_number": doc_no,
            "document_date": doc_date,
            "delivery_date": delivery_date,
            "partner_code": partner,
            "virtual_warehouse_code": loc,
            "items": items,
            "lines": lines,
        }, []

    def _parse_order(self, root):
        errors = []

        partner = self._get_text(root, "PARTNER")
        doc_no = self._get_text(root, "DOC_NO")
        doc_date = self._parse_date(self._get_text(root, "DOC_DATE"))
        delivery_date = self._parse_date(self._get_text(root, "DELIV_DATE"))
        loc = self._get_text(root, "LOC")
        is_delivery = self._get_text(root, "DELIV") == "1"
        delivery_address = self._get_text(root, "CONSIG_ADDR")

        if not partner:
            errors.append("PARTNER не указан")
        if not doc_no:
            errors.append("Номер документа не указан")

        items = []
        items_el = root.find("ITEMS")
        if items_el is not None:
            for item_el in items_el.findall("ITEM"):
                item_id = self._get_text(item_el, "ID")
                name = self._get_text(item_el, "NAME")
                if not item_id:
                    errors.append(f"{doc_no}: ID товара не указан")
                    continue
                items.append({
                    "external_id": item_id,
                    "name": name,
                })

        lines = []
        for ln_el in root.findall("LN"):
            item_id = self._get_text(ln_el, "ITEM")
            quantity = self._get_text(ln_el, "QNT")

            try:
                qty = int(quantity)
            except ValueError:
                errors.append(f"{doc_no}: Некорректное количество {quantity}")
                continue

            if qty <= 0:
                errors.append(f"{doc_no}: Количество должно быть больше 0")
                continue

            lines.append({
                "external_id": item_id,
                "quantity": qty,
            })

        if errors:
            return None, errors

        return {
            "document_type": "order",
            "document_number": doc_no,
            "document_date": doc_date,
            "delivery_date": delivery_date,
            "partner_code": partner,
            "virtual_warehouse_code": loc,
            "is_delivery": is_delivery,
            "delivery_address": delivery_address,
            "items": items,
            "lines": lines,
        }, []
