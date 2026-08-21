"""Адаптер доставки по email (заглушка)."""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any

from app.notifications.adapters.base import BaseAdapter

logger = logging.getLogger(__name__)

EMAIL_DIR = Path("logs/emails")


class EmailAdapter(BaseAdapter):
    """Сохраняет письма в файл (заглушка)."""

    channel = "email"

    async def send(self, recipient: dict[str, Any], notification: dict[str, Any]) -> None:
        """Сохранить письмо в файл."""
        EMAIL_DIR.mkdir(parents=True, exist_ok=True)

        email_to = recipient.get("email", "unknown@example.com")
        title = notification.get("title", "Без темы")
        text = notification.get("text", "")

        filename = EMAIL_DIR / f"email_{title.replace(' ', '_')}.txt"
        with open(filename, "a", encoding="utf-8") as f:
            f.write(f"Кому: {email_to}\n")
            f.write(f"Тема: {title}\n")
            f.write(f"Содержание:\n{text}\n")
            f.write("---\n")

        logger.info("Письмо сохранено: %s", filename)
