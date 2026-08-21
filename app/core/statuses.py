"""Enum статусов с русскими названиями для фронтенда."""

from __future__ import annotations

from enum import Enum


class OrderStatus(str, Enum):
    """Статусы заказов (InboundOrder, OutboundOrder)."""

    NEW = "new"
    DOCUMENT_CREATED = "document_created"
    TASK_CREATED = "task_created"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"

    @property
    def label(self) -> str:
        labels = {
            "new": "Новый",
            "document_created": "Документ создан",
            "task_created": "Задание создано",
            "in_progress": "В работе",
            "completed": "Завершен",
            "cancelled": "Отменен",
        }
        return labels.get(self.value, self.value)


class DocumentStatus(str, Enum):
    """Статусы складских документов."""

    DRAFT = "draft"
    TASK_CREATED = "task_created"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"

    @property
    def label(self) -> str:
        labels = {
            "draft": "Черновик",
            "task_created": "Задание создано",
            "in_progress": "В работе",
            "completed": "Завершен",
            "cancelled": "Отменен",
        }
        return labels.get(self.value, self.value)


class TaskStatus(str, Enum):
    """Статусы заданий."""

    NEW = "new"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    COMPLETED_WITH_DEVIATIONS = "completed_with_deviations"
    CANCELLED = "cancelled"

    @property
    def label(self) -> str:
        labels = {
            "new": "Новое",
            "in_progress": "В работе",
            "completed": "Завершено",
            "completed_with_deviations": "Завершено с отклонениями",
            "cancelled": "Отменено",
        }
        return labels.get(self.value, self.value)


class DeliveryStatus(str, Enum):
    """Статусы заявок на доставку."""

    CREATED = "created"
    ASSIGNED = "assigned"
    IN_TRANSIT = "in_transit"
    DELIVERED = "delivered"
    FAILED = "failed"

    @property
    def label(self) -> str:
        labels = {
            "created": "Создана",
            "assigned": "Назначена",
            "in_transit": "В пути",
            "delivered": "Доставлена",
            "failed": "Не доставлена",
        }
        return labels.get(self.value, self.value)
