"""Создание ролей по умолчанию."""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import select

from app.accounts.models import Role
from app.accounts.permissions_catalog import ACTIONS, CRUD, all_module_permissions
from app.core.database import async_session_factory


import app.accounts.models  # noqa: F401
import app.parties.models  # noqa: F401  # Depositor, Client для relationship

DEFAULT_ROLES = {
    "admin": {
        "name": "Администратор",
        "permissions": all_module_permissions(*ACTIONS),
    },
    "logist": {
        "name": "Логист",
        "permissions": {
            "delivery": list(CRUD),
            "routes": list(CRUD),
            "drivers": list(CRUD),
            "vehicles": list(CRUD),
            "addresses": ["view", "create", "update"],
            "orders": ["view", "create", "update"],
            "keepers": ["view"],
            "carriers": ["view"],
            "warehouse": ["view"],
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
            "warehouse": ["view"],
            "orders": ["view"],
            "notifications": ["view"],
            "files": ["view", "create"],
        },
    },
    "manager": {
        "name": "Менеджер",
        "permissions": {
            "clients": ["view", "create", "update"],
            "contracts": ["view", "create", "update"],
            "tariffs": ["view", "create", "update"],
            "orders": ["view", "create", "update"],
            "keepers": ["view"],
            "carriers": ["view", "create", "update"],
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
                select(Role).where(Role.code == code, Role.is_deleted.is_(False))
            )
            if existing:
                print(f"Роль {code} уже существует, обновляю права")
                existing.name = data["name"]
                existing.permissions = data["permissions"]
            else:
                print(f"Создаю роль: {code}")
                session.add(
                    Role(
                        name=data["name"],
                        code=code,
                        permissions=data["permissions"],
                    )
                )

        await session.commit()
        print("Готово!")


if __name__ == "__main__":
    asyncio.run(create_roles())
