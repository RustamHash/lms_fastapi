"""Проверка прав пользователя (не ORM-логика)."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.accounts.models.role import Role
    from app.accounts.models.user import User


def _alive_roles(user: "User") -> list["Role"]:
    roles = getattr(user, "roles", None) or []
    return [role for role in roles if not role.is_deleted]


def has_permission(user: "User", action: str, entity: str) -> bool:
    if user.is_superuser:
        return True
    if _has_extra_permission(user, action, entity):
        return True
    for role in _alive_roles(user):
        if _has_role_permission(role, action, entity):
            return True
    return False


def _has_extra_permission(user: "User", action: str, entity: str) -> bool:
    extra = user.extra_permissions or {}
    allowed = extra.get(entity, [])
    return action in allowed


def _has_role_permission(role: "Role", action: str, entity: str) -> bool:
    permissions = role.permissions or {}
    allowed = permissions.get(entity, [])
    return action in allowed


def get_all_permissions(user: "User") -> dict[str, list[str]]:
    if user.is_superuser:
        return {"all": ["all"]}

    result: dict[str, list[str]] = {}

    for role in _alive_roles(user):
        permissions = role.permissions or {}
        for entity, actions in permissions.items():
            bucket = result.setdefault(entity, [])
            for action in actions:
                if action not in bucket:
                    bucket.append(action)

    extra = user.extra_permissions or {}
    for entity, actions in extra.items():
        bucket = result.setdefault(entity, [])
        for action in actions:
            if action not in bucket:
                bucket.append(action)

    return result


def has_group_access(user: "User", entity: str) -> bool:
    if user.is_superuser:
        return True
    extra = user.extra_permissions or {}
    if extra.get(entity):
        return True
    for role in _alive_roles(user):
        permissions = role.permissions or {}
        if permissions.get(entity):
            return True
    return False
