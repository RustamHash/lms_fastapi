"""API для запуска импорта с подробным логом."""

from __future__ import annotations

import asyncio
import io
import logging
import time
from uuid import uuid4

from fastapi import APIRouter, Depends, Request
from pydantic import BaseModel
from fastapi.responses import StreamingResponse

from app.api.deps import SessionDep, UserDep, require_permission
from app.core.exceptions import NotFoundError
from app.integration.models import IntegrationLog

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
