"""Создание суперпользователя."""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from app.accounts.models import User
from app.accounts.repository import UserRepository
from app.core.database import async_session_factory
from app.core.security import hash_password


async def create_superuser(username: str, password: str, email: str = ""):
    async with async_session_factory() as session:
        repo = UserRepository(session)
        existing = await repo.get_by_username(username)
        if existing:
            print(f"Пользователь {username} уже существует")
            return

        user = User(
            username=username,
            password_hash=hash_password(password),
            email=email,
            is_superuser=True,
            is_active=True,
        )
        session.add(user)
        await session.commit()
        print(f"Суперпользователь {username} создан")


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Использование: python scripts/create_superuser.py <username> <password> [email]")
        sys.exit(1)

    username = sys.argv[1]
    password = sys.argv[2]
    email = sys.argv[3] if len(sys.argv) > 3 else ""

    asyncio.run(create_superuser(username, password, email))
