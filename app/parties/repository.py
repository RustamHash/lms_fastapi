# app/parties/repository.py

"""Репозитории для модуля parties."""

from __future__ import annotations


from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.infrastructure.repo_base import BaseRepository
from app.accounts.scope import DataScope
from app.parties.models import (
    Address,
    Carrier,
    Client,
    Contract,
    DeliveryZone,
    Depositor,
    Keeper,
    LegalEntity,
    RawAddress,
    Tariff,
    TariffDocument,
)


class AddressRepository(BaseRepository[Address]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, Address)

    async def get_by_fias_id(self, fias_id: str) -> Address | None:
        if not fias_id:
            return None
        stmt = select(Address).where(Address.fias_id == fias_id)
        return await self._s.scalar(stmt)

    async def get_by_full_address(self, full_address: str) -> Address | None:
        stmt = select(Address).where(Address.full_address == full_address)
        return await self._s.scalar(stmt)


class RawAddressRepository(BaseRepository[RawAddress]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, RawAddress)

    async def get_by_id(self, id: int) -> RawAddress | None:
        stmt = (
            select(RawAddress)
            .where(RawAddress.id == id)
            .options(selectinload(RawAddress.normalized_address))
        )
        return await self._s.scalar(stmt)

    async def list_all(self) -> list[RawAddress]:
        stmt = select(RawAddress).options(selectinload(RawAddress.normalized_address))
        return list(await self._s.scalars(stmt))

    async def get_by_hash(self, hash: str) -> RawAddress | None:
        stmt = (
            select(RawAddress)
            .where(RawAddress.hash == hash)
            .options(selectinload(RawAddress.normalized_address))
        )
        return await self._s.scalar(stmt)


class LegalEntityRepository(BaseRepository[LegalEntity]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, LegalEntity)


class ClientRepository(BaseRepository[Client]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, Client)

    async def get_by_id(self, id: int, scope: DataScope | None = None) -> Client | None:
        row = await super().get_by_id(id)
        if row is None:
            return None
        if scope is not None and not scope.allows_client(row.id, row.depositor_id):
            return None
        return row

    async def list_all(self, scope: DataScope | None = None) -> list[Client]:
        stmt = select(self._model)
        if scope is not None:
            stmt = scope.filter_client(stmt, Client.id, Client.depositor_id)
        return list(await self._s.scalars(stmt))

    async def get_by_code(
        self,
        depositor_id: int,
        code: str,
        delivery_address_id: int | None = None,
    ) -> Client | None:
        stmt = select(Client).where(
            Client.depositor_id == depositor_id,
            Client.code == code,
        )
        if delivery_address_id is None:
            stmt = stmt.where(Client.delivery_address_id.is_(None))
        else:
            stmt = stmt.where(Client.delivery_address_id == delivery_address_id)
        return await self._s.scalar(stmt)


class DepositorRepository(BaseRepository[Depositor]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, Depositor)


class ContractRepository(BaseRepository[Contract]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, Contract)


class TariffDocumentRepository(BaseRepository[TariffDocument]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, TariffDocument)


class TariffRepository(BaseRepository[Tariff]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, Tariff)


class DeliveryZoneRepository(BaseRepository[DeliveryZone]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, DeliveryZone)


class CarrierRepository(BaseRepository[Carrier]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, Carrier)


class KeeperRepository(BaseRepository[Keeper]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, Keeper)
