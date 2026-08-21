"""API для запуска импорта с подробным логом."""

from __future__ import annotations

import asyncio
import logging
import tempfile
import time

from fastapi import APIRouter, Depends
from sqlalchemy import select

from app.api.deps import SessionDep, UserDep, require_permission
from app.core.exceptions import NotFoundError
from app.integration.adapters import ZLNAdapter
from app.integration.models import IntegrationLog, IntegrationProfile
from app.integration.services.ftp_service import FTPService
from app.integration.services.integration_service import IntegrationService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/integrations", tags=["integrations"])


@router.post(
    "/import",
    dependencies=[Depends(require_permission("create", "integrations"))],
)
async def start_import(
    session: SessionDep,
    user_id: UserDep,
    document_type: str | None = None,
) -> dict:
    """Запустить импорт. Возвращает task_id."""
    
    import uuid

    # Общий task_id для всей задачи
    task_id = str(uuid.uuid4())

    asyncio.create_task(
        _run_import_background(task_id, user_id or 1, document_type)
    )

    return {"task_id": task_id, "status": "starting"}


async def _log_message(session, log: IntegrationLog, message: str, step: str = "") -> None:
    """Добавить сообщение в лог."""
    log.messages = (log.messages or []) + [message]
    if step:
        log.current_step = step
    await session.commit()


async def _log_error(session, log: IntegrationLog, error: str) -> None:
    """Добавить ошибку в лог."""
    log.errors = (log.errors or []) + [error]
    await session.commit()


async def _run_import_background(task_id: str, user_id: int, document_type: str | None) -> None:
    """Фоновый импорт: одна запись лога на каждый профиль."""
    from app.core.database import async_session_factory
    from uuid import uuid4

    async with async_session_factory() as session:
        try:
            # 1. Поиск активных профилей
            profiles = list(await session.scalars(
                select(IntegrationProfile).where(
                    IntegrationProfile.is_active.is_(True),
                    IntegrationProfile.is_deleted.is_(False),
                )
            ))

            if not profiles:
                log = IntegrationLog(
                    task_id=task_id,
                    status="failed",
                    document_type=document_type,
                    errors=["Нет активных профилей интеграции"],
                    created_by_id=user_id,
                    updated_by_id=user_id,
                )
                session.add(log)
                await session.commit()
                return

            # 2. Обработка каждого профиля отдельно
            adapter = ZLNAdapter()
            integration = IntegrationService(session)

            for profile in profiles:
                log = IntegrationLog(
                    task_id=task_id,
                    profile_id=profile.id,
                    status="processing",
                    document_type=document_type,
                    created_by_id=user_id,
                    updated_by_id=user_id,
                )
                session.add(log)
                await session.flush()
                await session.commit()

                ftp_config = profile.config.get("ftp", {})
                if not ftp_config:
                    log.errors = (log.errors or []) + [f"Профиль {profile.name}: нет FTP-конфигурации"]
                    log.status = "failed"
                    await session.commit()
                    continue

                await _log_message(session, log, f"Подключение к профилю: {profile.name} ({ftp_config.get('host', '')})", "Подключение")

                ftp = FTPService(
                    host=ftp_config["host"],
                    username=ftp_config["username"],
                    password=ftp_config["password"],
                )

                try:
                    ftp.connect()
                    await _log_message(session, log, f"Подключено: {ftp_config['host']}", "Подключено")

                    out_path = ftp_config.get("out_path", "/out")
                    files = ftp.list_files(out_path)
                    await _log_message(session, log, f"Найдено файлов: {len(files)}", "Файлы найдены")

                    log.total_rows = len(files)
                    await session.commit()

                    with tempfile.TemporaryDirectory() as tmp_dir:
                        for filename in files:
                            log.order_number = filename
                            await _log_message(session, log, f"Обработка файла: {filename}", "Обработка файла")

                            remote_path = f"{out_path}/{filename}"
                            local_path = ftp.download(remote_path, tmp_dir)

                            universal_doc, parse_errors = adapter.parse(local_path)
                            if parse_errors:
                                log.error_rows += 1
                                for err in parse_errors:
                                    await _log_error(session, log, f"Файл {filename}: {err}")
                                continue

                            doc_type = universal_doc.get("document_type")
                            doc_number = universal_doc.get("document_number")
                            log.order_number = doc_number

                            if document_type and doc_type != document_type:
                                continue

                            # Проверка дубликата
                            from app.orders.models import InboundOrder, OutboundOrder
                            existing = None
                            if doc_type == "porder":
                                existing = await session.scalar(
                                    select(InboundOrder).where(
                                        InboundOrder.depositor_id == profile.depositor_id,
                                        InboundOrder.number == doc_number,
                                    )
                                )
                            elif doc_type == "order":
                                existing = await session.scalar(
                                    select(OutboundOrder).where(
                                        OutboundOrder.depositor_id == profile.depositor_id,
                                        OutboundOrder.number == doc_number,
                                    )
                                )

                            if existing:
                                log.error_rows += 1
                                log.processed_rows += 1
                                await _log_error(session, log, f"Файл {filename}: Заказ {doc_number} уже существует")
                                await session.commit()
                                continue

                            # Лог по товарам
                            for item in universal_doc.get("items", []):
                                item_id = item.get("external_id")
                                await _log_message(session, log, f"Поиск товара: {item_id}", f"Поиск товара: {item_id}")

                            # Лог по клиенту/поставщику
                            if doc_type == "order":
                                customer_code = universal_doc.get("customer_code", "")
                                await _log_message(session, log, f"Поиск клиента: {customer_code}", f"Поиск клиента: {customer_code}")
                            elif doc_type == "porder":
                                vendor_code = universal_doc.get("vendor_code", "")
                                await _log_message(session, log, f"Поиск поставщика: {vendor_code}", f"Поиск поставщика: {vendor_code}")

                            await _log_message(session, log, f"Создание заказа: {doc_number}", f"Создание заказа: {doc_number}")

                            result, imp_errors = await integration.process_document(
                                universal_doc=universal_doc,
                                depositor_id=profile.depositor_id,
                                user_id=user_id,
                            )

                            log.processed_rows += 1
                            if imp_errors:
                                log.error_rows += 1
                                for err in imp_errors:
                                    await _log_error(session, log, f"Файл {filename}: {err}")
                            elif result:
                                log.success_rows += 1
                                await _log_message(session, log, f"Заказ {doc_number} создан успешно", f"Заказ создан: {doc_number}")
                                try:
                                    ftp.delete(remote_path)
                                    await _log_message(session, log, f"Файл {filename} удалён с FTP")
                                except Exception:
                                    pass

                            await session.commit()

                    log.status = "completed"
                    log.current_step = "Импорт завершен"
                    await _log_message(session, log, f"Импорт по профилю {profile.name} завершен. Успешно: {log.success_rows}, ошибок: {log.error_rows}", "Завершено")

                except Exception as e:
                    log.status = "failed"
                    await _log_error(session, log, f"Критическая ошибка: {e}")
                finally:
                    ftp.disconnect()

        except Exception as e:
            log = IntegrationLog(
                task_id=task_id,
                status="failed",
                document_type=document_type,
                errors=[str(e)],
                created_by_id=user_id,
                updated_by_id=user_id,
            )
            session.add(log)
            await session.commit()


@router.get(
    "/import/{task_id}/status",
    dependencies=[Depends(require_permission("view", "integrations"))],
)
async def get_import_status(task_id: str, session: SessionDep) -> dict:
    """Получить статус импорта."""
    log = await session.scalar(
        select(IntegrationLog).where(IntegrationLog.task_id == task_id)
    )
    if log is None:
        raise NotFoundError("Задача импорта не найдена")

    return _format_log(log)


@router.get(
    "/import/{task_id}/status/long",
    dependencies=[Depends(require_permission("view", "integrations"))],
)
async def get_import_status_long(task_id: str, session: SessionDep) -> dict:
    """Long Polling — держит до 25 сек, отвечает при изменениях."""
    start = time.time()
    last_messages_count = -1

    while time.time() - start < 25:
        log = await session.scalar(
            select(IntegrationLog).where(IntegrationLog.task_id == task_id)
        )
        if log is None:
            raise NotFoundError("Задача импорта не найдена")

        current_count = len(log.messages or [])

        if log.status in ("completed", "failed"):
            return _format_log(log)

        if current_count > last_messages_count:
            last_messages_count = current_count
            return _format_log(log)

        await asyncio.sleep(1)

    log = await session.scalar(
        select(IntegrationLog).where(IntegrationLog.task_id == task_id)
    )
    if log is None:
        raise NotFoundError("Задача импорта не найдена")

    return _format_log(log)


@router.get(
    "/import/history",
    dependencies=[Depends(require_permission("view", "integrations"))],
)
async def get_import_history(session: SessionDep) -> list[dict]:
    """История импортов."""
    logs = list(await session.scalars(
        select(IntegrationLog).order_by(IntegrationLog.created_at.desc()).limit(50)
    ))
    return [
        {
            "id": log.id,
            "task_id": log.task_id,
            "status": log.status,
            "document_type": log.document_type,
            "total_rows": log.total_rows,
            "success_rows": log.success_rows,
            "error_rows": log.error_rows,
            "created_at": log.created_at,
            "created_by_id": log.created_by_id,
        }
        for log in logs
    ]


def _format_log(log: IntegrationLog) -> dict:
    """Форматировать лог для ответа."""
    return {
        "task_id": log.task_id,
        "status": log.status,
        "document_type": log.document_type,
        "total_rows": log.total_rows,
        "processed_rows": log.processed_rows,
        "success_rows": log.success_rows,
        "error_rows": log.error_rows,
        "messages": log.messages or [],
        "errors": log.errors or [],
        "current_step": log.current_step or "",
        "order_number": log.order_number or "",
    }
