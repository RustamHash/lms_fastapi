"""Celery задачи."""

from __future__ import annotations

import asyncio
import logging
import os

from celery import Celery
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

logger = logging.getLogger(__name__)

celery_app = Celery(
    "lms",
    broker=os.getenv("REDIS_URL", "redis://localhost:6379/0"),
    backend=os.getenv("REDIS_URL", "redis://localhost:6379/1"),
)

celery_app.conf.update(
    task_routes={"app.tasks.run_import": {"queue": "imports"}},
    task_time_limit=600,
    task_soft_time_limit=540,
    task_acks_late=True,
    worker_prefetch_multiplier=1,
)


@celery_app.on_after_configure.connect
def _register_worker_subscribers(sender, **kwargs):
    """Delivery/export handlers: воркер не импортирует main.py."""
    from app.infrastructure.bootstrap_workers import bootstrap_background_subscribers

    bootstrap_background_subscribers()


@celery_app.task(name="app.tasks.run_import", bind=True, max_retries=3)
def run_import_task(self, task_id: str, user_id: int, document_type: str | None):
    """Задача импорта — Celery только ставит UoW-прогон, сущности не создаёт."""
    from app.infrastructure.bootstrap_workers import bootstrap_background_subscribers

    bootstrap_background_subscribers()
    from app.accounts.models import (  # noqa: F401
        User,
        Role,
        Audit,
        UserSettings,
        UserTableSettings,
        UserListPreset,
        UserDepositor,
        UserClient,
    )
    from app.parties.models import (  # noqa: F401
        Address,
        RawAddress,
        DeliveryZone,
        LegalEntity,
        Depositor,
        Keeper,
        Carrier,
        Client,
        Contract,
        TariffDocument,
        Tariff,
    )
    from app.warehouse.models import (  # noqa: F401
        Warehouse,
        VirtualWarehouse,
        Zone,
        Row,
        Location,
        ProductGroup,
        Product,
        Package,
        Batch,
        LPN,
        StockBalance,
        StockMovement,
        Task,
        TaskLine,
        ProductLocation,
    )
    from app.orders.models import (  # noqa: F401
        InboundOrder,
        InboundOrderLine,
        OutboundOrder,
        OutboundOrderLine,
        ReturnOrder,
        ReturnOrderLine,
    )
    from app.delivery.models import (  # noqa: F401
        DeliveryOrder,
        DeliveryDeviation,
        Driver,
        Vehicle,
        Route,
        RouteLine,
    )
    from app.documents.models import Document, DocumentLine  # noqa: F401
    from app.notifications.models import Notification, NotificationRule  # noqa: F401
    from app.files.models import File  # noqa: F401
    from app.integration.models import (  # noqa: F401
        IntegrationLog,
        IntegrationProfile,
        IntegrationError,
    )
    from app.core.context import set_current_user_id
    from app.core.database import create_worker_engine
    from app.infrastructure.uow import UnitOfWork
    from app.integration.repository import IntegrationLogRepository
    from app.integration.services.import_run_service import ImportRunService

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
                        from sqlalchemy.orm.attributes import flag_modified

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
