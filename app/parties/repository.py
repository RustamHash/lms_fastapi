# app/parties/repository.py

"""Репозитории для модуля parties."""

from __future__ import annotations

from typing import Any

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


def _address_opts():
    return (selectinload(Address.delivery_zone),)


def _legal_entity_opts():
    return (
        selectinload(LegalEntity.legal_address).selectinload(Address.delivery_zone),
        selectinload(LegalEntity.actual_address).selectinload(Address.delivery_zone),
    )


def _nested_legal_entity(attr):
    return selectinload(attr).options(*_legal_entity_opts())


def _contract_opts():
    return (
        _nested_legal_entity(Contract.customer),
        _nested_legal_entity(Contract.executor),
    )


def _depositor_opts():
    return (_nested_legal_entity(Depositor.legal_entity),)


def _client_opts():
    return (
        selectinload(Client.depositor).options(*_depositor_opts()),
        selectinload(Client.legal_address).selectinload(Address.delivery_zone),
        selectinload(Client.delivery_address).selectinload(Address.delivery_zone),
    )


def _tariff_document_opts():
    return (selectinload(TariffDocument.contract).options(*_contract_opts()),)


def _tariff_opts():
    return (selectinload(Tariff.document).options(*_tariff_document_opts()),)


class AddressRepository(BaseRepository[Address]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, Address)

    async def get_by_id(self, id: int) -> Address | None:
        stmt = select(Address).where(Address.id == id).options(*_address_opts())
        return await self._s.scalar(stmt)

    async def list_all(self) -> list[Address]:
        stmt = select(Address).options(*_address_opts())
        return list(await self._s.scalars(stmt))

    async def create(self, **kwargs: Any) -> Address:
        row = await super().create(**kwargs)
        return await self.get_by_id(row.id)  # type: ignore[return-value]

    async def update(self, id: int, **kwargs: Any) -> Address | None:
        if await super().update(id, **kwargs) is None:
            return None
        return await self.get_by_id(id)

    async def get_by_fias_id(self, fias_id: str) -> Address | None:
        if not fias_id:
            return None
        stmt = select(Address).where(Address.fias_id == fias_id).options(*_address_opts())
        return await self._s.scalar(stmt)

    async def get_by_full_address(self, full_address: str) -> Address | None:
        stmt = (
            select(Address)
            .where(Address.full_address == full_address)
            .options(*_address_opts())
        )
        return await self._s.scalar(stmt)


class RawAddressRepository(BaseRepository[RawAddress]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, RawAddress)

    def _opts(self):
        return (
            selectinload(RawAddress.normalized_address).selectinload(Address.delivery_zone),
        )

    async def get_by_id(self, id: int) -> RawAddress | None:
        stmt = select(RawAddress).where(RawAddress.id == id).options(*self._opts())
        return await self._s.scalar(stmt)

    async def list_all(self) -> list[RawAddress]:
        stmt = select(RawAddress).options(*self._opts())
        return list(await self._s.scalars(stmt))

    async def create(self, **kwargs: Any) -> RawAddress:
        row = await super().create(**kwargs)
        return await self.get_by_id(row.id)  # type: ignore[return-value]

    async def update(self, id: int, **kwargs: Any) -> RawAddress | None:
        if await super().update(id, **kwargs) is None:
            return None
        return await self.get_by_id(id)

    async def get_by_hash(self, hash: str) -> RawAddress | None:
        stmt = (
            select(RawAddress)
            .where(RawAddress.hash == hash)
            .options(*self._opts())
        )
        return await self._s.scalar(stmt)


class LegalEntityRepository(BaseRepository[LegalEntity]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, LegalEntity)

    async def get_by_id(self, id: int) -> LegalEntity | None:
        stmt = select(LegalEntity).where(LegalEntity.id == id).options(*_legal_entity_opts())
        return await self._s.scalar(stmt)

    async def list_all(self) -> list[LegalEntity]:
        stmt = select(LegalEntity).options(*_legal_entity_opts())
        return list(await self._s.scalars(stmt))

    async def create(self, **kwargs: Any) -> LegalEntity:
        row = await super().create(**kwargs)
        return await self.get_by_id(row.id)  # type: ignore[return-value]

    async def update(self, id: int, **kwargs: Any) -> LegalEntity | None:
        if await super().update(id, **kwargs) is None:
            return None
        return await self.get_by_id(id)


class ClientRepository(BaseRepository[Client]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, Client)

    async def get_by_id(self, id: int, scope: DataScope | None = None) -> Client | None:
        stmt = select(Client).where(Client.id == id).options(*_client_opts())
        row = await self._s.scalar(stmt)
        if row is None:
            return None
        if scope is not None and not scope.allows_client(row.id, row.depositor_id):
            return None
        return row

    async def list_all(self, scope: DataScope | None = None) -> list[Client]:
        stmt = select(Client).options(*_client_opts())
        if scope is not None:
            stmt = scope.filter_client(stmt, Client.id, Client.depositor_id)
        return list(await self._s.scalars(stmt))

    async def create(self, **kwargs: Any) -> Client:
        row = await super().create(**kwargs)
        return await self.get_by_id(row.id)  # type: ignore[return-value]

    async def update(self, id: int, **kwargs: Any) -> Client | None:
        if await super().update(id, **kwargs) is None:
            return None
        return await self.get_by_id(id)

    async def get_by_code(
        self,
        depositor_id: int,
        code: str,
        delivery_address_id: int | None = None,
    ) -> Client | None:
        stmt = select(Client).where(
            Client.depositor_id == depositor_id,
            Client.code == code,
        ).options(*_client_opts())
        if delivery_address_id is None:
            stmt = stmt.where(Client.delivery_address_id.is_(None))
        else:
            stmt = stmt.where(Client.delivery_address_id == delivery_address_id)
        return await self._s.scalar(stmt)


class DepositorRepository(BaseRepository[Depositor]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, Depositor)

    async def get_by_id(
        self,
        id: int,
        scope: DataScope | None = None,
        *,
        include_deleted: bool = False,
    ) -> Depositor | None:
        stmt = select(Depositor).where(Depositor.id == id).options(*_depositor_opts())
        if not include_deleted:
            stmt = stmt.where(Depositor.is_deleted.is_(False))
        if scope is not None:
            stmt = scope.filter_depositor(stmt, Depositor.id)
        return await self._s.scalar(stmt)

    async def list_all(self, scope: DataScope | None = None) -> list[Depositor]:
        stmt = (
            select(Depositor)
            .where(Depositor.is_deleted.is_(False))
            .options(*_depositor_opts())
        )
        if scope is not None:
            stmt = scope.filter_depositor(stmt, Depositor.id)
        return list(await self._s.scalars(stmt))

    async def create(self, **kwargs: Any) -> Depositor:
        row = await super().create(**kwargs)
        return await self.get_by_id(row.id)  # type: ignore[return-value]

    async def update(self, id: int, **kwargs: Any) -> Depositor | None:
        if await super().update(id, **kwargs) is None:
            return None
        return await self.get_by_id(id)


class ContractRepository(BaseRepository[Contract]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, Contract)

    async def get_by_id(self, id: int) -> Contract | None:
        stmt = select(Contract).where(Contract.id == id).options(*_contract_opts())
        return await self._s.scalar(stmt)

    async def list_all(self) -> list[Contract]:
        stmt = select(Contract).options(*_contract_opts())
        return list(await self._s.scalars(stmt))

    async def create(self, **kwargs: Any) -> Contract:
        row = await super().create(**kwargs)
        return await self.get_by_id(row.id)  # type: ignore[return-value]

    async def update(self, id: int, **kwargs: Any) -> Contract | None:
        if await super().update(id, **kwargs) is None:
            return None
        return await self.get_by_id(id)


class TariffDocumentRepository(BaseRepository[TariffDocument]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, TariffDocument)

    async def get_by_id(self, id: int) -> TariffDocument | None:
        stmt = (
            select(TariffDocument)
            .where(TariffDocument.id == id)
            .options(*_tariff_document_opts())
        )
        return await self._s.scalar(stmt)

    async def list_all(self) -> list[TariffDocument]:
        stmt = select(TariffDocument).options(*_tariff_document_opts())
        return list(await self._s.scalars(stmt))

    async def create(self, **kwargs: Any) -> TariffDocument:
        row = await super().create(**kwargs)
        return await self.get_by_id(row.id)  # type: ignore[return-value]

    async def update(self, id: int, **kwargs: Any) -> TariffDocument | None:
        if await super().update(id, **kwargs) is None:
            return None
        return await self.get_by_id(id)


class TariffRepository(BaseRepository[Tariff]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, Tariff)

    async def get_by_id(self, id: int) -> Tariff | None:
        stmt = select(Tariff).where(Tariff.id == id).options(*_tariff_opts())
        return await self._s.scalar(stmt)

    async def list_all(self) -> list[Tariff]:
        stmt = select(Tariff).options(*_tariff_opts())
        return list(await self._s.scalars(stmt))

    async def create(self, **kwargs: Any) -> Tariff:
        row = await super().create(**kwargs)
        return await self.get_by_id(row.id)  # type: ignore[return-value]

    async def update(self, id: int, **kwargs: Any) -> Tariff | None:
        if await super().update(id, **kwargs) is None:
            return None
        return await self.get_by_id(id)


class DeliveryZoneRepository(BaseRepository[DeliveryZone]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, DeliveryZone)


class CarrierRepository(BaseRepository[Carrier]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, Carrier)

    async def get_by_id(self, id: int) -> Carrier | None:
        stmt = select(Carrier).where(Carrier.id == id).options(
            _nested_legal_entity(Carrier.legal_entity)
        )
        return await self._s.scalar(stmt)

    async def list_all(self) -> list[Carrier]:
        stmt = select(Carrier).options(_nested_legal_entity(Carrier.legal_entity))
        return list(await self._s.scalars(stmt))

    async def create(self, **kwargs: Any) -> Carrier:
        row = await super().create(**kwargs)
        return await self.get_by_id(row.id)  # type: ignore[return-value]

    async def update(self, id: int, **kwargs: Any) -> Carrier | None:
        if await super().update(id, **kwargs) is None:
            return None
        return await self.get_by_id(id)


class KeeperRepository(BaseRepository[Keeper]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, Keeper)

    async def get_by_id(self, id: int) -> Keeper | None:
        stmt = select(Keeper).where(Keeper.id == id).options(
            _nested_legal_entity(Keeper.legal_entity)
        )
        return await self._s.scalar(stmt)

    async def list_all(self) -> list[Keeper]:
        stmt = select(Keeper).options(_nested_legal_entity(Keeper.legal_entity))
        return list(await self._s.scalars(stmt))

    async def create(self, **kwargs: Any) -> Keeper:
        row = await super().create(**kwargs)
        return await self.get_by_id(row.id)  # type: ignore[return-value]

    async def update(self, id: int, **kwargs: Any) -> Keeper | None:
        if await super().update(id, **kwargs) is None:
            return None
        return await self.get_by_id(id)
