"""Прогон импорта: FTP, адаптер, вызов принятия заявки. Без создания заказа."""

from __future__ import annotations

import logging
import tempfile
from dataclasses import dataclass

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.core.exceptions import BadRequestError
from app.infrastructure.uow import UnitOfWork
from app.integration.adapters import ZLNAdapter
from app.integration.models import IntegrationLog
from app.integration.repository import IntegrationLogRepository, IntegrationProfileRepository
from app.integration.services.ftp_service import FTPService
from app.orders.services.inbound_exchange_service import inbound_exchange_from_session

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class _ProfileFtp:
    name: str
    depositor_id: int
    host: str
    username: str
    password: str
    out_path: str


class ImportRunService:
    def __init__(self, session_factory: async_sessionmaker[AsyncSession]) -> None:
        self._factory = session_factory

    async def run(
        self, task_id: str, user_id: int, document_type: str | None
    ) -> None:
        profiles = await self._prepare(task_id, user_id, document_type)
        if profiles is None:
            return

        adapter = ZLNAdapter()
        for profile in profiles:
            await self._run_profile(task_id, user_id, document_type, adapter, profile)

        async with UnitOfWork(self._factory) as session:
            log = await IntegrationLogRepository(session).get_by_task_id(task_id)
            if log is None:
                return
            log.status = "completed"
            log.current_step = "Импорт завершён"
            log.messages = (log.messages or []) + ["Импорт завершён"]

    async def _prepare(
        self, task_id: str, user_id: int, document_type: str | None
    ) -> list[_ProfileFtp] | None:
        async with UnitOfWork(self._factory) as session:
            logs = IntegrationLogRepository(session)
            log = await logs.get_by_task_id(task_id)
            if log is None:
                log = await logs.create(
                    task_id=task_id,
                    status="processing",
                    document_type=document_type,
                    created_by_id=user_id,
                )
            log.status = "processing"

            profiles = await IntegrationProfileRepository(session).list_active()
            logger.info("Найдено профилей: %d", len(profiles))
            if not profiles:
                log.status = "failed"
                log.errors = ["Нет активных профилей интеграции"]
                return None

            result: list[_ProfileFtp] = []
            for profile in profiles:
                ftp_config = (profile.config or {}).get("ftp") or {}
                if not ftp_config:
                    log.errors = (log.errors or []) + [
                        f"Профиль {profile.name}: нет FTP-конфигурации"
                    ]
                    log.status = "failed"
                    continue
                result.append(
                    _ProfileFtp(
                        name=profile.name,
                        depositor_id=profile.depositor_id,
                        host=ftp_config["host"],
                        username=ftp_config["username"],
                        password=ftp_config["password"],
                        out_path=ftp_config.get("out_path", "/out"),
                    )
                )
            if not result:
                log.status = "failed"
                if not log.errors:
                    log.errors = ["Нет профилей с FTP-конфигурацией"]
                return None
            return result

    async def _run_profile(
        self,
        task_id: str,
        user_id: int,
        document_type: str | None,
        adapter: ZLNAdapter,
        profile: _ProfileFtp,
    ) -> None:
        logger.info("Обработка профиля: %s", profile.name)
        ftp = FTPService(profile.host, profile.username, profile.password)
        try:
            ftp.connect()
            all_files = ftp.list_files(profile.out_path)
            if document_type == "order":
                files = [f for f in all_files if f.startswith("order_")]
            elif document_type == "porder":
                files = [f for f in all_files if f.startswith("porder_")]
            else:
                files = all_files

            async with UnitOfWork(self._factory) as session:
                log = await self._require_log(session, task_id)
                if not files:
                    message = (
                        f"Нет файлов типа '{document_type}_*' на FTP. "
                        f"Всего файлов: {len(all_files)}"
                    )
                    log.status = "failed"
                    log.errors = (log.errors or []) + [message]
                    log.messages = (log.messages or []) + [message]
                    log.current_step = "Файлы не найдены"
                    return
                log.total_rows = (log.total_rows or 0) + len(files)
                log.messages = (log.messages or []) + [f"Найдено файлов: {len(files)}"]
                log.current_step = "Обработка файлов"

            for filename in files:
                remote_path = f"{profile.out_path}/{filename}"
                remove_ftp = False
                with tempfile.TemporaryDirectory() as tmp_dir:
                    local_path = ftp.download(remote_path, tmp_dir)
                    async with UnitOfWork(self._factory) as session:
                        remove_ftp = await self._process_file(
                            session,
                            task_id=task_id,
                            user_id=user_id,
                            adapter=adapter,
                            profile=profile,
                            filename=filename,
                            local_path=local_path,
                        )
                if remove_ftp:
                    try:
                        ftp.delete(remote_path)
                    except Exception:
                        logger.warning(
                            "Не удалось удалить %s с FTP", remote_path, exc_info=True
                        )
        except Exception as e:
            logger.error("Ошибка импорта: %s", e, exc_info=True)
            async with UnitOfWork(self._factory) as session:
                log = await self._require_log(session, task_id)
                log.status = "failed"
                log.errors = (log.errors or []) + [str(e)]
        finally:
            try:
                ftp.disconnect()
            except Exception:
                pass

    async def _process_file(
        self,
        session: AsyncSession,
        *,
        task_id: str,
        user_id: int,
        adapter: ZLNAdapter,
        profile: _ProfileFtp,
        filename: str,
        local_path: str,
    ) -> bool:
        """Вернуть True, если файл можно снять с FTP (успех или пропуск PORDER)."""
        log = await self._require_log(session, task_id)
        message, parse_errors = await adapter.parse(local_path)

        if parse_errors:
            log.processed_rows = (log.processed_rows or 0) + 1
            log.error_rows = (log.error_rows or 0) + 1
            log.errors = (log.errors or []) + parse_errors
            return False

        if message is None:
            log.processed_rows = (log.processed_rows or 0) + 1
            log.error_rows = (log.error_rows or 0) + 1
            log.errors = (log.errors or []) + ["Ошибка парсинга: пустой документ"]
            return False

        exchange = inbound_exchange_from_session(session)
        try:
            result = await exchange.accept(
                depositor_id=profile.depositor_id,
                message=message,
                user_id=user_id,
            )
        except BadRequestError as e:
            await session.rollback()
            log = await self._require_log(session, task_id)
            log.processed_rows = (log.processed_rows or 0) + 1
            log.error_rows = (log.error_rows or 0) + 1
            log.errors = (log.errors or []) + [str(e.detail)]
            return False

        log.processed_rows = (log.processed_rows or 0) + 1
        is_porder_file = filename.lower().startswith("porder_")
        if result.skipped:
            log.messages = (log.messages or []) + [
                f"Заказ {message.number} уже есть, пропуск"
            ]
            return is_porder_file

        log.success_rows = (log.success_rows or 0) + 1
        log.messages = (log.messages or []) + [f"Заказ {message.number} создан"]
        return is_porder_file

    async def _require_log(
        self, session: AsyncSession, task_id: str
    ) -> IntegrationLog:
        log = await IntegrationLogRepository(session).get_by_task_id(task_id)
        if log is None:
            raise RuntimeError(f"Журнал импорта {task_id} не найден")
        return log
