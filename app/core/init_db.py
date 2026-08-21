"""Инициализация БД: создание системного пользователя и суперпользователя."""

from __future__ import annotations

import logging

from sqlalchemy import select

from app.accounts.models import User
from app.core.security import hash_password

logger = logging.getLogger(__name__)


async def init_db(session) -> None:
    """Создать базовых пользователей, если их нет."""
    
    # 1. Системный пользователь для фоновых задач
    system_user = await session.scalar(
        select(User).where(User.username == "system_bot")
    )
    if system_user is None:
        system_user = User(
            username="system_bot",
            password_hash=hash_password("system_bot_secret"),
            email="system@local",
            is_superuser=False,
            is_active=True,
        )
        session.add(system_user)
        await session.flush()
        logger.info("Создан системный пользователь: system_bot (id=%s)", system_user.id)
    else:
        logger.info("Системный пользователь уже существует (id=%s)", system_user.id)

    # 2. Суперпользователь
    admin_user = await session.scalar(
        select(User).where(User.username == "admin")
    )
    if admin_user is None:
        admin_user = User(
            username="admin",
            password_hash=hash_password("admin"),
            email="admin@local",
            is_superuser=True,
            is_active=True,
        )
        session.add(admin_user)
        await session.flush()
        logger.info("Создан суперпользователь: admin (id=%s)", admin_user.id)
    else:
        logger.info("Суперпользователь уже существует (id=%s)", admin_user.id)

    await session.commit()
