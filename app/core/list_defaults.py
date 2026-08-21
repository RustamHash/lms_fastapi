"""Заводские конфигурации списков."""

from __future__ import annotations

DEFAULT_PREFS: dict[str, dict] = {
    "clients": {
        "order": ["id", "name", "inn", "is_active"],
        "hidden": [],
        "widths": {},
        "filters": {},
        "exclude_filters": {},
        "sort": None,
        "quick_filters": ["name"],
    },
    "products": {
        "order": ["id", "name", "sku", "price"],
        "hidden": [],
        "widths": {},
        "filters": {},
        "exclude_filters": {},
        "sort": None,
        "quick_filters": ["name"],
    },
    "documents": {
        "order": ["id", "document_number", "document_date", "status"],
        "hidden": [],
        "widths": {},
        "filters": {},
        "exclude_filters": {},
        "sort": {"column": "document_date", "direction": "desc"},
        "quick_filters": ["status"],
    },
    "delivery_orders": {
        "order": ["id", "number", "delivery_date", "status"],
        "hidden": [],
        "widths": {},
        "filters": {},
        "exclude_filters": {},
        "sort": {"column": "delivery_date", "direction": "desc"},
        "quick_filters": ["status"],
    },
    "tasks": {
        "order": ["id", "task_type", "status", "assignee_id"],
        "hidden": [],
        "widths": {},
        "filters": {},
        "exclude_filters": {},
        "sort": None,
        "quick_filters": ["status"],
    },
}


def get_default_prefs(entity_key: str) -> dict:
    """Возвращает заводские настройки для сущности."""
    defaults = DEFAULT_PREFS.get(entity_key)
    if defaults is None:
        return {
            "order": [],
            "hidden": [],
            "widths": {},
            "filters": {},
            "exclude_filters": {},
            "sort": None,
            "quick_filters": [],
        }
    return defaults


def merge_with_defaults(prefs: dict, entity_key: str) -> dict:
    """Дополняет prefs недостающими полями из заводских."""
    defaults = get_default_prefs(entity_key)
    merged = {**defaults, **prefs}
    for key, value in defaults.items():
        if key not in merged or merged[key] is None:
            merged[key] = value
    return merged
