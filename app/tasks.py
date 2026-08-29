"""Celery-приложение: очередь импорта."""

from __future__ import annotations

import asyncio
import logging

from celery import Celery
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker
from sqlalchemy.orm.attributes import flag_modified

from app.core.config import get_settings
from app.infrastructure.logging import setup_logging

logger = logging.getLogger(__name__)

settings = get_settings()
setup_logging(settings)

celery_app = Celery(
    "lms",
    broker=settings.resolve_celery_broker_url(),
    backend=settings.resolve_celery_result_backend(),
)

celery_app.conf.update(
    task_routes={
        "app.tasks.run_import": {"queue": "imports"},
        "app.tasks.ensure_delivery_for_outbound": {"queue": "imports"},
    },
    task_time_limit=600,
    task_soft_time_limit=540,
    task_acks_late=True,
    worker_prefetch_multiplier=1,
)


@celery_app.on_after_configure.connect
def _register_worker_subscribers(sender, **kwargs):
    """Воркер не импортирует main.py — подписчики здесь."""
    from app.infrastructure.bootstrap_workers import bootstrap_background_subscribers

    bootstrap_background_subscribers()


@celery_app.task(name="app.tasks.run_import")
def run_import_task(task_id: str, user_id: int, document_type: str | None):
    """Celery только запускает ImportRunService; сущности создаёт сервис в своих UoW.

    Статус для UI — IntegrationLog, не Celery result. При сбое задача
    завершается SUCCESS для Celery после записи failed в лог (без fake retry).
    """
    import app.models_registry  # noqa: F401
    from app.core.context import set_current_user_id
    from app.core.database import create_worker_engine
    from app.infrastructure.bootstrap_workers import bootstrap_background_subscribers
    from app.infrastructure.uow import UnitOfWork
    from app.integration.repository import IntegrationLogRepository
    from app.integration.services.import_run_service import ImportRunService

    bootstrap_background_subscribers()

    async def run_import() -> None:
        engine = create_worker_engine()
        factory = async_sessionmaker(
            engine, class_=AsyncSession, expire_on_commit=False
        )
        try:
            set_current_user_id(user_id)
            await ImportRunService(factory).run(task_id, user_id, document_type)
        except Exception as exc:
            logger.exception("Сбой импорта %s", task_id)
            try:
                async with UnitOfWork(factory) as session:
                    log = await IntegrationLogRepository(session).get_by_task_id(task_id)
                    if log is not None:
                        log.status = "failed"
                        log.current_step = "Сбой воркера"
                        log.errors = list(log.errors or []) + [str(exc)]
                        log.messages = list(log.messages or []) + [
                            f"Воркер остановился с ошибкой: {exc}"
                        ]
                        flag_modified(log, "errors")
                        flag_modified(log, "messages")
            except Exception:
                logger.exception("Не удалось записать сбой импорта %s в журнал", task_id)
        finally:
            await engine.dispose()

    asyncio.run(run_import())


@celery_app.task(name="app.tasks.ensure_delivery_for_outbound")
def ensure_delivery_for_outbound(order_id: int):
    """Повторное создание DeliveryOrder после сбоя in-process handler."""
    import app.models_registry  # noqa: F401
    from app.core.database import create_worker_engine
    from app.delivery.services.from_outbound_service import (
        delivery_from_outbound_from_session,
    )
    from app.infrastructure.bootstrap_workers import bootstrap_background_subscribers
    from app.infrastructure.uow import UnitOfWork

    bootstrap_background_subscribers()

    async def run() -> None:
        engine = create_worker_engine()
        factory = async_sessionmaker(
            engine, class_=AsyncSession, expire_on_commit=False
        )
        try:
            async with UnitOfWork(factory) as session:
                delivery = await delivery_from_outbound_from_session(
                    session
                ).ensure_for_outbound(order_id)
                logger.info(
                    "Celery ensure_delivery_for_outbound(%s) → %s",
                    order_id,
                    delivery.id if delivery else None,
                )
        finally:
            await engine.dispose()

    asyncio.run(run())
