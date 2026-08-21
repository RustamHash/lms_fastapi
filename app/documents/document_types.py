"""Типы складских документов."""

from __future__ import annotations

from enum import Enum


class DocumentType(str, Enum):
    """Типы складских документов."""

    RECEIPT = "receipt"  # Приходная накладная
    SHIPMENT = "shipment"  # Отгрузка
    MOVEMENT = "movement"  # Перемещение
    INVENTORY = "inventory"  # Инвентаризация
    ADJUSTMENT = "adjustment"  # Корректировка

    @property
    def label(self) -> str:
        """Русское название типа."""
        labels = {
            "receipt": "Приходная накладная",
            "shipment": "Отгрузка",
            "movement": "Перемещение",
            "inventory": "Инвентаризация",
            "adjustment": "Корректировка",
        }
        return labels.get(self.value, self.value)
