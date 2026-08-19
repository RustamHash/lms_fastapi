"""Настройка логирования."""

from __future__ import annotations

import logging
import logging.config
from pathlib import Path

from app.core.config import Settings


class MaxLevelFilter(logging.Filter):
    """Фильтр — пропускает только записи до max_level включительно."""

    def __init__(self, max_level: int) -> None:
        super().__init__()
        self.max_level = max_level

    def filter(self, record: logging.LogRecord) -> bool:
        return record.levelno <= self.max_level


def setup_logging(settings: Settings) -> None:
    """Инициализация логирования."""
    _ensure_log_dirs(
        settings.app_log_file_path,
        settings.error_log_file_path,
        settings.sql_log_file_path,
    )

    log_level = _normalize_level(settings.log_level)
    sql_level = "DEBUG" if settings.debug_sql else "ERROR"

    config = {
        "version": 1,
        "disable_existing_loggers": False,
        "filters": {
            "max_info_warning": {"()": MaxLevelFilter, "max_level": logging.WARNING}
        },
        "formatters": {
            "default": {
                "format": "%(asctime)s | %(levelname)s | %(name)s | %(message)s",
            }
        },
        "handlers": {
            "stdout": {
                "class": "logging.StreamHandler",
                "formatter": "default",
                "level": log_level,
            },
            "app_file": {
                "class": "logging.handlers.RotatingFileHandler",
                "formatter": "default",
                "filename": settings.app_log_file_path,
                "maxBytes": 10 * 1024 * 1024,
                "backupCount": 5,
                "encoding": "utf-8",
                "level": log_level,
                "filters": ["max_info_warning"],
            },
            "error_file": {
                "class": "logging.handlers.RotatingFileHandler",
                "formatter": "default",
                "filename": settings.error_log_file_path,
                "maxBytes": 10 * 1024 * 1024,
                "backupCount": 5,
                "encoding": "utf-8",
                "level": "ERROR",
            },
            "sql_file": {
                "class": "logging.handlers.RotatingFileHandler",
                "formatter": "default",
                "filename": settings.sql_log_file_path,
                "maxBytes": 10 * 1024 * 1024,
                "backupCount": 5,
                "encoding": "utf-8",
                "level": sql_level,
            },
        },
        "root": {
            "level": log_level,
            "handlers": ["stdout", "app_file", "error_file"],
        },
        "loggers": {
            "uvicorn": {
                "handlers": ["stdout", "app_file", "error_file"],
                "level": log_level,
            },
            "uvicorn.error": {
                "handlers": ["stdout", "app_file", "error_file"],
                "level": log_level,
                "propagate": False,
            },
            "uvicorn.access": {
                "handlers": ["stdout", "app_file", "error_file"],
                "level": log_level,
                "propagate": False,
            },
            "sqlalchemy.engine": {
                "handlers": ["sql_file"],
                "level": sql_level,
                "propagate": False,
            },
            "sqlalchemy.pool": {
                "handlers": ["sql_file"],
                "level": sql_level,
                "propagate": False,
            },
        },
    }
    logging.config.dictConfig(config)


def _normalize_level(raw_level: str) -> str:
    level = (raw_level or "").strip().upper()
    return level if level in {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"} else "INFO"


def _ensure_log_dirs(*file_paths: str) -> None:
    for path in file_paths:
        directory = Path(path).expanduser().resolve().parent
        directory.mkdir(parents=True, exist_ok=True)
