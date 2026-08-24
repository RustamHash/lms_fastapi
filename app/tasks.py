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
    """Задача импорта — выполняется в Celery worker."""
    from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
    from app.core.config import get_settings
    from app.core.context import set_current_user_id

    from app.accounts.models import (
        User,
        Role,
        Audit,
        UserSettings,
        UserTableSettings,
        UserListPreset,
        UserDepositor,
    )
    from app.parties.models import (
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
    from app.warehouse.models import (
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
    from app.orders.models import (
        InboundOrder,
        InboundOrderLine,
        OutboundOrder,
        OutboundOrderLine,
        ReturnOrder,
        ReturnOrderLine,
    )
    from app.delivery.models import (
        DeliveryOrder,
        DeliveryDeviation,
        Driver,
        Vehicle,
        Route,
        RouteLine,
    )
    from app.documents.models import Document, DocumentLine
    from app.notifications.models import Notification, NotificationRule
    from app.files.models import File
    from app.integration.models import (
        IntegrationLog,
        IntegrationProfile,
        IntegrationError,
    )
    from app.integration.services.ftp_service import FTPService
    from app.integration.adapters import ZLNAdapter
    from app.integration.services.integration_service import IntegrationService
    from sqlalchemy import select
    import tempfile
    import logging

    logger = logging.getLogger(__name__)
    settings = get_settings()

    async def run_import():
        set_current_user_id(user_id)

        engine = create_async_engine(settings.database_url)
        session_factory = async_sessionmaker(
            engine, expire_on_commit=False, autoflush=False
        )

        async with session_factory() as session:
            logger.info("Начало импорта: task_id=%s, type=%s", task_id, document_type)

            try:
                log = await session.scalar(
                    select(IntegrationLog).where(IntegrationLog.task_id == task_id)
                )

                if log is None:
                    log = IntegrationLog(
                        task_id=task_id,
                        status="processing",
                        document_type=document_type,
                        created_by_id=user_id,
                    )
                    session.add(log)
                    await session.commit()

                log.status = "processing"
                await session.commit()

                profiles = list(
                    await session.scalars(
                        select(IntegrationProfile).where(
                            IntegrationProfile.is_active.is_(True),
                        )
                    )
                )
                logger.info("Найдено профилей: %d", len(profiles))

                if not profiles:
                    log.status = "failed"
                    log.errors = ["Нет активных профилей интеграции"]
                    await session.commit()
                    return

                adapter = ZLNAdapter()
                integration = IntegrationService(session)

                for profile in profiles:
                    logger.info("Обработка профиля: %s", profile.name)

                    ftp_config = profile.config.get("ftp", {})

                    if not ftp_config:
                        log.errors = (log.errors or []) + [
                            f"Профиль {profile.name}: нет FTP-конфигурации"
                        ]
                        log.status = "failed"
                        await session.commit()
                        continue

                    ftp = FTPService(
                        host=ftp_config["host"],
                        username=ftp_config["username"],
                        password=ftp_config["password"],
                    )

                    try:
                        logger.info("Подключение к FTP: %s", ftp_config["host"])
                        ftp.connect()
                        logger.info("FTP подключен")

                        out_path = ftp_config.get("out_path", "/out")
                        all_files = ftp.list_files(out_path)
                        logger.info("Файлов на FTP: %d", len(all_files))

                        if document_type == "order":
                            files = [f for f in all_files if f.startswith("order_")]
                        elif document_type == "porder":
                            files = [f for f in all_files if f.startswith("porder_")]
                        else:
                            files = all_files

                        logger.info("Отфильтровано файлов: %d", len(files))

                        if not files:
                            message = (
                                f"Нет файлов типа '{document_type}_*' на FTP. "
                                f"Всего файлов: {len(all_files)}"
                            )
                            logger.warning(message)
                            log.status = "failed"
                            log.errors = (log.errors or []) + [message]
                            log.messages = (log.messages or []) + [message]
                            log.current_step = "Файлы не найдены"
                            await session.commit()
                            continue

                        log.total_rows = len(files)
                        log.messages = (log.messages or []) + [
                            f"Найдено файлов: {len(files)}"
                        ]
                        log.current_step = "Обработка файлов"
                        await session.commit()

                        for filename in files:
                            logger.info("Обработка файла: %s", filename)

                            remote_path = f"{out_path}/{filename}"

                            with tempfile.TemporaryDirectory() as tmp_dir:
                                local_path = ftp.download(remote_path, tmp_dir)
                                universal_doc, parse_errors = await adapter.parse(
                                    local_path
                                )

                                if parse_errors:
                                    log.error_rows += 1
                                    for err in parse_errors:
                                        log.errors = (log.errors or []) + [err]
                                    await session.commit()
                                    continue

                                if universal_doc is None:
                                    log.error_rows += 1
                                    log.errors = (log.errors or []) + [
                                        "Ошибка парсинга: пустой документ"
                                    ]
                                    await session.commit()
                                    continue

                                doc_number = universal_doc.get("document_number")

                                result, imp_errors = await integration.process_document(
                                    universal_doc=universal_doc,
                                    depositor_id=profile.depositor_id,
                                    user_id=user_id,
                                )

                                log.processed_rows += 1

                                if imp_errors:
                                    log.error_rows += 1
                                    for err in imp_errors:
                                        log.errors = (log.errors or []) + [err]
                                else:
                                    log.success_rows += 1
                                    log.messages = (log.messages or []) + [
                                        f"Заказ {doc_number} создан"
                                    ]

                                await session.commit()

                        log.status = "completed"
                        log.current_step = "Импорт завершён"
                        log.messages = (log.messages or []) + ["Импорт завершён"]
                        await session.commit()

                    except Exception as e:
                        logger.error("Ошибка импорта: %s", e, exc_info=True)
                        log.status = "failed"
                        log.errors = (log.errors or []) + [str(e)]
                        await session.commit()
                    finally:
                        try:
                            ftp.disconnect()
                        except Exception:
                            pass

            except Exception as e:
                logger.error("Критическая ошибка: %s", e, exc_info=True)

        await engine.dispose()

    asyncio.run(run_import())
