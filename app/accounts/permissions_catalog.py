"""Единый каталог модулей и действий RBAC."""

from __future__ import annotations

# Коды модулей = entity в require_permission(..., entity)
MODULES: tuple[str, ...] = (
    "users",
    "roles",
    "audit",
    "addresses",
    "legal_entities",
    "depositors",
    "keepers",
    "carriers",
    "clients",
    "contracts",
    "tariffs",
    "products",
    "batches",
    "lpns",
    "stock",
    "tasks",
    "warehouse",
    "orders",
    "documents",
    "delivery",
    "drivers",
    "vehicles",
    "routes",
    "notifications",
    "integrations",
    "files",
)

MODULE_LABELS: dict[str, str] = {
    "users": "Пользователи",
    "roles": "Роли",
    "audit": "Аудит",
    "addresses": "Адреса",
    "legal_entities": "Юрлица",
    "depositors": "Поклажедатели",
    "keepers": "Хранители",
    "carriers": "Перевозчики",
    "clients": "Клиенты",
    "contracts": "Договоры",
    "tariffs": "Тарифы",
    "products": "Товары",
    "batches": "Партии",
    "lpns": "LPN",
    "stock": "Остатки",
    "tasks": "Задания",
    "warehouse": "Топология склада",
    "orders": "Заказы",
    "documents": "Документы",
    "delivery": "Доставка",
    "drivers": "Водители",
    "vehicles": "Транспорт",
    "routes": "Маршруты",
    "notifications": "Уведомления",
    "integrations": "Интеграции",
    "files": "Файлы",
}

ACTIONS: tuple[str, ...] = (
    "view",
    "create",
    "update",
    "delete",
    "execute",
    "complete",
    "approve",
    "cancel",
)

ACTION_LABELS: dict[str, str] = {
    "view": "Просмотр",
    "create": "Создание",
    "update": "Изменение",
    "delete": "Удаление",
    "execute": "Выполнение",
    "complete": "Завершение",
    "approve": "Согласование",
    "cancel": "Отмена",
}

CRUD: tuple[str, ...] = ("view", "create", "update", "delete")


def validate_permissions_map(permissions: dict[str, list[str]]) -> dict[str, list[str]]:
    """Проверяет, что все модули и действия есть в каталоге."""
    modules = set(MODULES)
    actions = set(ACTIONS)
    for entity, entity_actions in permissions.items():
        if entity not in modules:
            raise ValueError(f"Неизвестный модуль: {entity}")
        for action in entity_actions:
            if action not in actions:
                raise ValueError(f"Неизвестное действие: {action} для модуля {entity}")
    return permissions


def all_module_permissions(*actions: str) -> dict[str, list[str]]:
    """Права на все модули с заданными действиями."""
    chosen = list(actions) if actions else list(ACTIONS)
    return {module: list(chosen) for module in MODULES}
