"""Celery задачи."""

from __future__ import annotations

import asyncio
import os

from celery import Celery

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


@celery_app.task(name="app.tasks.run_import", bind=True, max_retries=3)
def run_import_task(self, task_id: str, user_id: int, document_type: str | None):
    """Задача импорта — Celery только ставит UoW-прогон, сущности не создаёт."""
    from app.accounts.models import (  # noqa: F401
        User,
        Role,
        Audit,
        UserSettings,
        UserTableSettings,
        UserListPreset,
        UserDepositor,
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
    from app.core.database import async_session_factory
    from app.integration.services.import_run_service import ImportRunService

    async def run_import():
        set_current_user_id(user_id)
        await ImportRunService(async_session_factory).run(
            task_id, user_id, document_type
        )

    asyncio.run(run_import())
