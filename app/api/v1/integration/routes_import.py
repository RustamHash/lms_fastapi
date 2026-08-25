"""API для запуска импорта с подробным логом."""

from __future__ import annotations

import asyncio
import io
import logging
import tempfile
import time
from datetime import datetime, timezone
from uuid import uuid4

from fastapi import APIRouter, Depends, Request
from pydantic import BaseModel
from fastapi.responses import StreamingResponse
from sqlalchemy import select

from app.api.deps import SessionDep, UserDep, require_permission
from app.core.context import set_current_user_id
from app.core.exceptions import NotFoundError
from app.infrastructure.events import event_bus
from app.infrastructure.events.event_types import EventTypes
from app.integration.adapters import ZLNAdapter
from app.integration.models import IntegrationLog, IntegrationProfile
from app.integration.services.ftp_service import FTPService
from app.integration.services.integration_service import IntegrationService

logger = logging.getLogger(__name__)


class ImportRequest(BaseModel):
    """Тело запроса для импорта."""

    document_type: str | None = None
    documentType: str | None = None


router = APIRouter(prefix="/integrations", tags=["integrations"])


@router.post(
    "/import",
    dependencies=[Depends(require_permission("create", "integrations"))],
)
async def start_import(
    request: Request,
    session: SessionDep,
    user_id: UserDep,
    body: ImportRequest | None = None,
) -> dict:
    """Запустить импорт. Возвращает task_id."""
    # Извлечь document_type из body или query
    document_type = None
    if body:
        document_type = body.document_type or body.documentType

    logger.info("ПОЛУЧЕН ЗАПРОС: document_type=%s, user_id=%s", document_type, user_id)

    # Общий task_id для всей задачи
    task_id = str(uuid4())

    # Создаём запись в логе СРАЗУ, чтобы фронтенд мог получить статус
    from app.integration.repository import IntegrationLogRepository

    await IntegrationLogRepository(session).create(
        task_id=task_id,
        status="starting",
        document_type=document_type,
        created_by_id=user_id,
    )

    # Отправляем задачу в Celery
    from app.tasks import celery_app

    celery_task = celery_app.send_task(
        "app.tasks.run_import",
        args=[task_id, user_id or 1, document_type],
    )
    return {
        "task_id": task_id,
        "celery_task_id": celery_task.id,
        "status": "queued",
    }


async def _log_message(
    session, log: IntegrationLog, message: str, step: str = ""
) -> None:
    """Добавить сообщение в лог."""
    log.messages = (log.messages or []) + [message]
    if step:
        log.current_step = step
    await session.commit()


async def _log_error(session, log: IntegrationLog, error: str) -> None:
    """Добавить ошибку в лог."""
    log.errors = (log.errors or []) + [error]
    await session.commit()


async def _run_import_background(
    task_id: str, user_id: int, document_type: str | None
) -> None:
    """Фоновый импорт."""
    set_current_user_id(user_id)

    from app.core.database import async_session_factory

    session = async_session_factory()

    logger.info("Начало импорта: task_id=%s, type=%s", task_id, document_type)

    try:
        # Найти или создать лог
        log = await IntegrationLogRepository(session).get_by_task_id(task_id)

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
        logger.info("Лог обновлён: processing")

        # 1. Поиск активных профилей
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
            await session.close()
            return

        # 2. Обработка каждого профиля
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
                await ftp.connect()
                logger.info("FTP подключен")

                out_path = ftp_config.get("out_path", "/out")
                all_files = await ftp.list_files(out_path)
                logger.info("Файлов на FTP: %d", len(all_files))

                # Фильтруем по типу документа
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
                log.messages = (log.messages or []) + [f"Найдено файлов: {len(files)}"]
                log.current_step = "Обработка файлов"
                await session.commit()

                # Обработка каждого файла
                for filename in files:
                    logger.info("Обработка файла: %s", filename)

                    remote_path = f"{out_path}/{filename}"

                    with tempfile.TemporaryDirectory() as tmp_dir:
                        local_path = await ftp.download(remote_path, tmp_dir)
                        universal_doc, parse_errors = await adapter.parse(local_path)

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

                        result, imp_errors, skipped = await integration.process_document(
                            universal_doc=universal_doc,
                            depositor_id=profile.depositor_id,
                            user_id=user_id,
                        )

                        log.processed_rows += 1

                        if skipped:
                            log.messages = (log.messages or []) + [
                                f"Заказ {doc_number} уже есть, пропуск"
                            ]
                        elif imp_errors:
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

                await event_bus.emit(
                    EventTypes.IMPORT_COMPLETED,
                    {
                        "_event_type": EventTypes.IMPORT_COMPLETED,
                        "success_rows": log.success_rows,
                        "error_rows": log.error_rows,
                    },
                )

            except Exception as e:
                logger.error("Ошибка импорта: %s", e, exc_info=True)
                log.status = "failed"
                log.errors = (log.errors or []) + [str(e)]
                await session.commit()
            finally:
                try:
                    await ftp.disconnect()
                except Exception:
                    pass

        await session.close()

    except Exception as e:
        logger.error("Критическая ошибка: %s", e, exc_info=True)
        try:
            await session.rollback()
            await session.close()
        except Exception:
            pass


@router.get(
    "/import/{task_id}/status",
    dependencies=[Depends(require_permission("view", "integrations"))],
)
async def get_import_status(task_id: str, session: SessionDep) -> dict:
    """Получить статус импорта."""
    from app.integration.repository import IntegrationLogRepository

    log = await IntegrationLogRepository(session).get_by_task_id(task_id)
    if log is None:
        raise NotFoundError("Задача импорта не найдена")
    return _format_log(log)


@router.get(
    "/import/{task_id}/status/long",
    dependencies=[Depends(require_permission("view", "integrations"))],
)
async def get_import_status_long(task_id: str, session: SessionDep) -> dict:
    """Long Polling — держит до 25 сек, отвечает при изменениях."""
    from app.integration.repository import IntegrationLogRepository

    start = time.time()
    last_messages_count = -1

    while time.time() - start < 25:
        log = await IntegrationLogRepository(session).get_by_task_id(task_id)
        if log is None:
            raise NotFoundError("Задача импорта не найдена")

        current_count = len(log.messages or [])

        if log.status in ("completed", "failed"):
            return _format_log(log)

        if current_count > last_messages_count:
            last_messages_count = current_count
            return _format_log(log)

        await asyncio.sleep(1)

    from app.integration.repository import IntegrationLogRepository

    log = await IntegrationLogRepository(session).get_by_task_id(task_id)
    if log is None:
        raise NotFoundError("Задача импорта не найдена")
    return _format_log(log)


@router.get(
    "/import/history",
    dependencies=[Depends(require_permission("view", "integrations"))],
)
async def get_import_history(session: SessionDep) -> list[dict]:
    """История импортов."""
    from app.integration.repository import IntegrationLogRepository

    logs = await IntegrationLogRepository(session).list_all()
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


@router.get(
    "/import/{task_id}/errors/excel",
    dependencies=[Depends(require_permission("view", "integrations"))],
)
async def download_import_errors_excel(task_id: str, session: SessionDep):
    """Скачать Excel файл с ошибками импорта."""
    from openpyxl import Workbook
    from openpyxl.worksheet.worksheet import Worksheet

    from app.integration.repository import IntegrationLogRepository

    log = await IntegrationLogRepository(session).get_by_task_id(task_id)
    if log is None:
        raise NotFoundError("Задача импорта не найдена")

    logs = [log]

    wb = Workbook()
    ws: Worksheet | None = wb.active

    if ws is None:
        raise RuntimeError("Не удалось создать лист Excel")

    ws.title = "Ошибки импорта"

    headers = ["Файл", "Ошибка", "Профиль", "Дата"]
    ws.append(headers)

    for log in logs:
        profile_name = log.profile.name if log.profile else "Все профили"
        for error in log.errors or []:
            file_name = log.order_number or ""
            error_text = error

            if error.startswith("Файл "):
                parts = error.split(": ", 1)
                if len(parts) == 2:
                    file_name = parts[0].replace("Файл ", "")
                    error_text = parts[1]

            ws.append(
                [
                    file_name,
                    error_text,
                    profile_name,
                    (
                        log.created_at.strftime("%Y-%m-%d %H:%M:%S")
                        if log.created_at
                        else ""
                    ),
                ]
            )

    total_errors = sum(len(log.errors or []) for log in logs)
    if total_errors == 0:
        ws.append(["", "Ошибок нет", "", ""])

    output = io.BytesIO()
    wb.save(output)
    output.seek(0)

    filename = f"import_errors_{task_id[:8]}.xlsx"

    return StreamingResponse(
        output,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f"attachment; filename={filename}"},
    )


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
