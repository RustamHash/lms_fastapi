"""Выгрузка ответного XML Зиландии на FTP out_path."""

from __future__ import annotations

import logging
from dataclasses import dataclass
from decimal import Decimal

from sqlalchemy.ext.asyncio import AsyncSession

from app.integration.exporters.zln_xml import (
    ExportLine,
    build_desadv,
    build_ordrsp,
    build_pordrsp,
    build_recadv,
)
from app.integration.repository import IntegrationProfileRepository
from app.integration.services.ftp_service import FTPService
from app.orders.repository import InboundOrderRepository, OutboundOrderRepository
from app.warehouse.repository import TaskLineRepository

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class _FtpOut:
    host: str
    username: str
    password: str
    out_path: str
    partner: str


class ExportService:
    def __init__(self, session: AsyncSession) -> None:
        self._s = session
        self._profiles = IntegrationProfileRepository(session)
        self._inbound = InboundOrderRepository(session)
        self._outbound = OutboundOrderRepository(session)
        self._task_lines = TaskLineRepository(session)

    async def export_pordrsp(self, order_id: int) -> bool:
        order = await self._inbound.get_by_id(order_id)
        if order is None:
            logger.warning("PORDRSP: inbound #%s не найден", order_id)
            return False
        if order.pordrsp_exported:
            return True
        ftp = await self._ftp_out(order.depositor_id)
        if ftp is None:
            return False
        name, body = build_pordrsp(
            partner=ftp.partner,
            doc_no=order.number,
            order_date=order.order_date,
        )
        if not self._upload(ftp, name, body):
            return False
        order.pordrsp_exported = True
        await self._s.flush()
        logger.info("PORDRSP выгружен для %s → %s", order.number, name)
        return True

    async def export_ordrsp(self, order_id: int) -> bool:
        order = await self._outbound.get_by_id(order_id)
        if order is None:
            logger.warning("ORDRSP: outbound #%s не найден", order_id)
            return False
        if order.ordrsp_exported:
            return True
        ftp = await self._ftp_out(order.depositor_id)
        if ftp is None:
            return False
        name, body = build_ordrsp(
            partner=ftp.partner,
            doc_no=order.number,
            order_date=order.order_date,
        )
        if not self._upload(ftp, name, body):
            return False
        order.ordrsp_exported = True
        await self._s.flush()
        logger.info("ORDRSP выгружен для %s → %s", order.number, name)
        return True

    async def export_recadv(self, *, order_id: int, task_id: int) -> bool:
        order = await self._inbound.get_by_id(order_id)
        if order is None:
            logger.warning("RECADV: inbound #%s не найден", order_id)
            return False
        if order.recadv_exported:
            return True
        ftp = await self._ftp_out(order.depositor_id)
        if ftp is None:
            return False
        lines = self._export_lines(await self._task_lines.list_by_task(task_id))
        name, body = build_recadv(
            partner=ftp.partner,
            doc_no=order.number,
            order_date=order.order_date,
            lines=lines,
        )
        if not self._upload(ftp, name, body):
            return False
        order.recadv_exported = True
        await self._s.flush()
        logger.info("RECADV выгружен для %s → %s", order.number, name)
        return True

    async def export_desadv(self, *, order_id: int, task_id: int) -> bool:
        order = await self._outbound.get_by_id(order_id)
        if order is None:
            logger.warning("DESADV: outbound #%s не найден", order_id)
            return False
        if order.desadv_exported:
            return True
        ftp = await self._ftp_out(order.depositor_id)
        if ftp is None:
            return False
        lines = self._export_lines(await self._task_lines.list_by_task(task_id))
        name, body = build_desadv(
            partner=ftp.partner,
            doc_no=order.number,
            order_date=order.order_date,
            lines=lines,
        )
        if not self._upload(ftp, name, body):
            return False
        order.desadv_exported = True
        await self._s.flush()
        logger.info("DESADV выгружен для %s → %s", order.number, name)
        return True

    async def _ftp_out(self, depositor_id: int) -> _FtpOut | None:
        profile = await self._profiles.get_active_with_out_path(depositor_id)
        if profile is None:
            logger.warning(
                "Нет активного профиля с out_path для поклажедателя #%s",
                depositor_id,
            )
            return None
        ftp = (profile.config or {}).get("ftp") or {}
        host = str(ftp.get("host") or "").strip()
        out_path = str(ftp.get("out_path") or "").strip()
        if not host or not out_path:
            logger.warning(
                "Профиль «%s»: нет host/out_path для выгрузки", profile.name
            )
            return None
        partner = str(
            (profile.config or {}).get("partner")
            or ftp.get("partner")
            or "ZLN"
        ).strip() or "ZLN"
        return _FtpOut(
            host=host,
            username=str(ftp.get("username") or ""),
            password=str(ftp.get("password") or ""),
            out_path=out_path,
            partner=partner,
        )

    @staticmethod
    def _upload(ftp_cfg: _FtpOut, filename: str, body: bytes) -> bool:
        ftp = FTPService(ftp_cfg.host, ftp_cfg.username, ftp_cfg.password)
        try:
            ftp.connect()
            ftp.upload(ftp_cfg.out_path, filename, body)
            return True
        except Exception:
            logger.exception(
                "FTP upload %s/%s не удался", ftp_cfg.out_path, filename
            )
            return False
        finally:
            try:
                ftp.disconnect()
            except Exception:
                pass

    @staticmethod
    def _export_lines(task_lines) -> list[ExportLine]:
        result: list[ExportLine] = []
        for line in task_lines:
            if line.fact_qty is None or line.fact_qty <= 0:
                continue
            product = line.product
            batch = line.batch
            qty = line.fact_qty
            if not isinstance(qty, Decimal):
                qty = Decimal(str(qty))
            result.append(
                ExportLine(
                    item=product.external_id if product else "",
                    lot=batch.batch_number if batch else "",
                    date_exp=batch.expiration_date if batch else None,
                    unit="шт",
                    quantity=qty,
                )
            )
        return result


def export_from_session(session: AsyncSession) -> ExportService:
    return ExportService(session)
