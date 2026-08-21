"""Создание ролей по умолчанию."""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from app.accounts.models import Role
from app.core.database import async_session_factory

DEFAULT_ROLES = {
    "admin": {
        "name": "Администратор",
        "permissions": {
            "users": ["view", "create", "update", "delete"],
            "roles": ["view", "create", "update", "delete"],
            "audit": ["view"],
            "addresses": ["view", "create", "update", "delete"],
            "legal_entities": ["view", "create", "update", "delete"],
            "depositors": ["view", "create", "update", "delete"],
            "clients": ["view", "create", "update", "delete"],
            "trade_points": ["view", "create", "update", "delete"],
            "contracts": ["view", "create", "update", "delete"],
            "tariffs": ["view", "create", "update", "delete"],
            "products": ["view", "create", "update", "delete"],
            "batches": ["view", "create", "update", "delete"],
            "lpns": ["view", "create", "update", "delete"],
            "stock": ["view", "create", "update", "delete"],
            "tasks": ["view", "create", "update", "delete", "execute", "complete"],
            "documents": ["view", "create", "update", "delete", "approve"],
            "delivery": ["view", "create", "update", "delete"],
            "drivers": ["view", "create", "update", "delete"],
            "vehicles": ["view", "create", "update", "delete"],
            "routes": ["view", "create", "update", "delete"],
            "notifications": ["view", "create", "update"],
            "integrations": ["view", "create", "update", "delete"],
            "files": ["view", "create", "update", "delete"],
        },
    },
    "logist": {
        "name": "Логист",
        "permissions": {
            "delivery": ["view", "create", "update", "delete"],
            "routes": ["view", "create", "update", "delete"],
            "drivers": ["view", "create", "update", "delete"],
            "vehicles": ["view", "create", "update", "delete"],
            "addresses": ["view", "create", "update"],
            "trade_points": ["view", "create", "update"],
            "notifications": ["view"],
            "files": ["view", "create"],
        },
    },
    "operator": {
        "name": "Оператор",
        "permissions": {
            "products": ["view"],
            "batches": ["view"],
            "lpns": ["view", "create"],
            "stock": ["view", "create", "update"],
            "tasks": ["view", "execute", "complete"],
            "documents": ["view", "create", "update"],
            "notifications": ["view"],
            "files": ["view", "create"],
        },
    },
    "manager": {
        "name": "Менеджер",
        "permissions": {
            "clients": ["view", "create", "update"],
            "trade_points": ["view", "create", "update"],
            "contracts": ["view", "create", "update"],
            "tariffs": ["view", "create", "update"],
            "documents": ["view", "create", "update", "approve"],
            "delivery": ["view", "create", "update"],
            "notifications": ["view", "create"],
            "files": ["view", "create"],
        },
    },
}


async def create_roles():
    async with async_session_factory() as session:
        for code, data in DEFAULT_ROLES.items():
            existing = await session.scalar(
                __import__("sqlalchemy").select(Role).where(Role.code == code)
            )
            if existing:
                print(f"Роль {code} уже существует, обновляю права")
                existing.name = data["name"]
                existing.permissions = data["permissions"]
            else:
                print(f"Создаю роль: {code}")
                role = Role(
                    name=data["name"],
                    code=code,
                    permissions=data["permissions"],
                )
                session.add(role)
        
        await session.commit()
        print("Готово!")


if __name__ == "__main__":
    asyncio.run(create_roles())
