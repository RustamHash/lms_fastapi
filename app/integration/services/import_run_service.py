"""Прогон импорта: FTP, адаптер, вызов принятия заявки. Без создания заказа."""

from __future__ import annotations

import logging
import tempfile
from dataclasses import dataclass

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker
from sqlalchemy.orm.attributes import flag_modified

from app.core.exceptions import BadRequestError
from app.infrastructure.uow import UnitOfWork
from app.integration.adapters import ZLNAdapter
from app.integration.models import IntegrationLog
from app.integration.repository import IntegrationLogRepository, IntegrationProfileRepository
from app.integration.services.ftp_service import FTPService
from app.orders.exchange_messages import InboundExchangeMessage, OutboundExchangeMessage
from app.orders.services.inbound_exchange_service import inbound_exchange_from_session
from app.orders.services.outbound_exchange_service import outbound_exchange_from_session

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class _ProfileFtp:
    name: str
    depositor_id: int
    host: str
    username: str
    password: str
    in_path: str


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
            has_ok = (log.success_rows or 0) > 0
            has_errors = bool(log.errors)
            log.status = "failed" if has_errors and not has_ok else "completed"
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
            log.current_step = "Ищем профили"
            type_label = document_type or "все"
            log.messages = (log.messages or []) + [
                f"Задача принята, тип документов: {type_label}",
                "Ищем активные профили интеграции",
            ]

            profiles = await IntegrationProfileRepository(session).list_active()
            logger.info("Найдено профилей: %d", len(profiles))
            if not profiles:
                log.status = "failed"
                log.current_step = "Нет профилей"
                log.errors = ["Нет активных профилей интеграции"]
                log.messages = (log.messages or []) + [
                    "Активных профилей интеграции нет"
                ]
                return None

            log.messages = (log.messages or []) + [
                f"Найдено активных профилей: {len(profiles)}"
            ]

            result: list[_ProfileFtp] = []
            for profile in profiles:
                ftp_config = (profile.config or {}).get("ftp") or {}
                if not ftp_config:
                    msg = f"Профиль «{profile.name}»: нет настроек FTP"
                    log.errors = (log.errors or []) + [msg]
                    log.messages = (log.messages or []) + [msg]
                    continue
                in_path = str(ftp_config.get("in_path") or "").strip()
                if not in_path:
                    msg = f"Профиль «{profile.name}»: нет папки входящих (in_path)"
                    log.errors = (log.errors or []) + [msg]
                    log.messages = (log.messages or []) + [msg]
                    continue
                host = str(ftp_config.get("host") or "").strip()
                username = str(ftp_config.get("username") or "")
                password = str(ftp_config.get("password") or "")
                if not host:
                    msg = f"Профиль «{profile.name}»: не указан FTP-хост"
                    log.errors = (log.errors or []) + [msg]
                    log.messages = (log.messages or []) + [msg]
                    continue
                result.append(
                    _ProfileFtp(
                        name=profile.name,
                        depositor_id=profile.depositor_id,
                        host=host,
                        username=username,
                        password=password,
                        in_path=in_path,
                    )
                )

            if not result:
                log.status = "failed"
                log.current_step = "Нет FTP"
                if not log.errors:
                    log.errors = ["Нет профилей с FTP-конфигурацией"]
                log.messages = (log.messages or []) + [
                    "Подходящих настроек FTP нет — импорт остановлен"
                ]
                return None

            depositors = {p.depositor_id for p in result}
            log.messages = (log.messages or []) + [
                (
                    f"С FTP и папкой входящих: {len(result)} "
                    f"(поклажедателей: {len(depositors)})"
                )
            ]
            log.current_step = "Подключение к FTP"
            return result

    async def _run_profile(
        self,
        task_id: str,
        user_id: int,
        document_type: str | None,
        adapter: ZLNAdapter,
        profile: _ProfileFtp,
    ) -> None:
        await self._emit(
            task_id,
            message=(
                f"Профиль «{profile.name}», поклажедатель #{profile.depositor_id}: "
                f"подключаемся к FTP {profile.host}, каталог {profile.in_path}"
            ),
            step=f"FTP: {profile.name}",
        )
        ftp = FTPService(profile.host, profile.username, profile.password)
        try:
            ftp.connect()
            await self._emit(
                task_id,
                message=f"Профиль «{profile.name}»: подключение к FTP успешно",
            )
            all_files = ftp.list_files(profile.in_path)
            if document_type == "order":
                files = [f for f in all_files if f.startswith("order_")]
            elif document_type == "porder":
                files = [f for f in all_files if f.startswith("porder_")]
            else:
                files = all_files

            if not files:
                message = (
                    f"Профиль «{profile.name}»: в {profile.in_path} нет файлов "
                    f"типа '{document_type}_*' (всего в каталоге: {len(all_files)})"
                )
                await self._emit(task_id, message=message, step="Файлы не найдены")
                return

            await self._emit(
                task_id,
                message=(
                    f"Профиль «{profile.name}»: в каталоге {len(all_files)} файлов, "
                    f"к обработке {len(files)}"
                ),
                step="Обработка файлов",
            )
            async with UnitOfWork(self._factory) as session:
                log = await self._require_log(session, task_id)
                log.total_rows = (log.total_rows or 0) + len(files)

            for filename in files:
                await self._emit(
                    task_id,
                    message=f"Обрабатываем файл {filename}",
                    step=filename,
                )
                remote_path = f"{profile.in_path}/{filename}"
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
            await self._emit(
                task_id,
                message=f"Профиль «{profile.name}»: ошибка FTP — {e}",
                error=str(e),
                step="Ошибка FTP",
            )
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
        """Вернуть True, если файл можно снять с FTP (успех или пропуск)."""
        log = await self._require_log(session, task_id)
        message, parse_errors = await adapter.parse(local_path)

        if parse_errors:
            log.processed_rows = (log.processed_rows or 0) + 1
            log.error_rows = (log.error_rows or 0) + 1
            log.errors = (log.errors or []) + parse_errors
            log.messages = (log.messages or []) + [
                f"Файл {filename}: {err}" for err in parse_errors
            ]
            return False

        if message is None:
            log.processed_rows = (log.processed_rows or 0) + 1
            log.error_rows = (log.error_rows or 0) + 1
            empty = f"Файл {filename}: пустой документ"
            log.errors = (log.errors or []) + [empty]
            log.messages = (log.messages or []) + [empty]
            return False

        try:
            if isinstance(message, OutboundExchangeMessage):
                result = await outbound_exchange_from_session(session).accept(
                    depositor_id=profile.depositor_id,
                    message=message,
                    user_id=user_id,
                )
            elif isinstance(message, InboundExchangeMessage):
                result = await inbound_exchange_from_session(session).accept(
                    depositor_id=profile.depositor_id,
                    message=message,
                    user_id=user_id,
                )
            else:
                raise BadRequestError(f"Неизвестный тип сообщения: {type(message)}")
        except BadRequestError as e:
            await session.rollback()
            log = await self._require_log(session, task_id)
            log.processed_rows = (log.processed_rows or 0) + 1
            log.error_rows = (log.error_rows or 0) + 1
            detail = str(e.detail) if getattr(e, "detail", None) else str(e)
            log.errors = (log.errors or []) + [detail]
            log.messages = (log.messages or []) + [f"Файл {filename}: {detail}"]
            return False

        log.processed_rows = (log.processed_rows or 0) + 1
        can_remove = filename.lower().startswith(("porder_", "order_"))
        if result.skipped:
            log.messages = (log.messages or []) + [
                f"Файл {filename}: заявка {message.number} уже есть, пропуск"
            ]
            return can_remove

        log.success_rows = (log.success_rows or 0) + 1
        log.messages = (log.messages or []) + [
            f"Файл {filename}: заявка {message.number} создана"
        ]
        return can_remove

    async def _emit(
        self,
        task_id: str,
        *,
        message: str | None = None,
        error: str | None = None,
        step: str | None = None,
    ) -> None:
        async with UnitOfWork(self._factory) as session:
            log = await self._require_log(session, task_id)
            if message:
                log.messages = list(log.messages or []) + [message]
                flag_modified(log, "messages")
            if error:
                log.errors = list(log.errors or []) + [error]
                flag_modified(log, "errors")
            if step:
                log.current_step = step

    async def _require_log(
        self, session: AsyncSession, task_id: str
    ) -> IntegrationLog:
        log = await IntegrationLogRepository(session).get_by_task_id(task_id)
        if log is None:
            raise RuntimeError(f"Журнал импорта {task_id} не найден")
        return log
