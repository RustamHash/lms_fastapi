
from __future__ import annotations

import asyncio
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import select

from app.accounts.models import User
from app.core.database import async_session_factory
from app.core.security import hash_password

import app.accounts.models  # noqa: F401
import app.parties.models  # noqa: F401  # Depositor, Client для relationship


async def _ensure_user(
    session,
    *,
    username: str,
    password: str,
    email: str | None,
    is_superuser: bool,
) -> str:
    existing = await session.scalar(select(User).where(User.username == username))
    if existing is not None:
        return f"уже есть: {username} (id={existing.id})"

    user = User(
        username=username,
        password_hash=hash_password(password),
        email=email,
        is_superuser=is_superuser,
        is_active=True,
    )
    session.add(user)
    await session.flush()
    return f"создан: {username} (id={user.id})"


async def bootstrap() -> None:
    admin_username = os.getenv("LMS_ADMIN_USERNAME", "admin")
    admin_password = os.getenv("LMS_ADMIN_PASSWORD", "admin123")
    admin_email = os.getenv("LMS_ADMIN_EMAIL", "admin@local") or None
    system_password = os.getenv("LMS_SYSTEM_BOT_PASSWORD", "system_bot_secret")

    async with async_session_factory() as session:
        msg_bot = await _ensure_user(
            session,
            username="system_bot",
            password=system_password,
            email="system@local",
            is_superuser=False,
        )
        msg_admin = await _ensure_user(
            session,
            username=admin_username,
            password=admin_password,
            email=admin_email,
            is_superuser=True,
        )
        await session.commit()

    print(msg_bot)
    print(msg_admin)


if __name__ == "__main__":
    asyncio.run(bootstrap())
