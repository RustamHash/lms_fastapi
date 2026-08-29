"""Регистрация всех ORM-моделей для процессов без полного import графа (Celery, скрипты)."""

from __future__ import annotations

import app.accounts.models  # noqa: F401
import app.delivery.models  # noqa: F401
import app.documents.models  # noqa: F401
import app.files.models  # noqa: F401
import app.integration.models  # noqa: F401
import app.notifications.models  # noqa: F401
import app.orders.models  # noqa: F401
import app.parties.models  # noqa: F401
import app.warehouse.models  # noqa: F401
