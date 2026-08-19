"""Базовый адаптер."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class BaseAdapter(ABC):
    """Базовый класс адаптера для парсинга файлов."""

    @abstractmethod
    def parse(self, file_path: str) -> tuple[Any | None, list[str]]:
        """Парсинг файла. Возвращает (данные, ошибки)."""
        ...
