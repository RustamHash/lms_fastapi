"""Репозитории для модуля parties."""

from __future__ import annotations

from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession

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


class AddressRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_address_by_id(self, address_id: int) -> Address | None:
        return await self.session.get(Address, address_id)

    async def get_by_hash(self, address_hash: str) -> Address | None:
        if not address_hash:
            return None
        stmt = (
            select(Address)
            .join(RawAddress, RawAddress.normalized_address_id == Address.id)
            .where(RawAddress.hash == address_hash)
        )
        return await self.session.scalar(stmt)

    async def list_addresses(self) -> list[Address]:
        stmt = select(Address).where()
        return list(await self.session.scalars(stmt))

    async def insert_address(self, **kwargs) -> Address:
        row = Address(**kwargs)
        self.session.add(row)
        await self.session.flush()
        return row

    async def find_raw_by_text(self, raw_text: str) -> RawAddress | None:
        stmt = select(RawAddress).where(
            RawAddress.raw_text == raw_text,
        )
        return await self.session.scalar(stmt)

    async def find_address_by_fias_id(self, fias_id: str) -> Address | None:
        if not fias_id:
            return None
        stmt = select(Address).where(
            Address.fias_id == fias_id,
        )
        return await self.session.scalar(stmt)

    async def find_address_by_full_address(self, full_address: str) -> Address | None:
        if not full_address:
            return None
        stmt = select(Address).where(
            Address.full_address == full_address,
        )
        return await self.session.scalar(stmt)

    async def insert_raw(self, **kwargs) -> RawAddress:
        row = RawAddress(**kwargs)
        self.session.add(row)
        await self.session.flush()
        return row


class LegalEntityRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_by_id(self, entity_id: int) -> LegalEntity | None:
        return await self.session.get(LegalEntity, entity_id)

    async def get_by_inn(self, inn: str) -> LegalEntity | None:
        if not inn:
            return None
        stmt = select(LegalEntity).where(
            LegalEntity.inn == inn)
        return await self.session.scalar(stmt)

    async def list_all(self) -> list[LegalEntity]:
        stmt = select(LegalEntity).where()
        return list(await self.session.scalars(stmt))

    async def insert(self, **kwargs) -> LegalEntity:
        row = LegalEntity(**kwargs)
        self.session.add(row)
        await self.session.flush()
        return row

    async def update(self, entity_id: int, **kwargs) -> LegalEntity | None:
        row = await self.session.get(LegalEntity, entity_id)
        if row is None:
            return None
        for field, value in kwargs.items():
            setattr(row, field, value)
        await self.session.flush()
        return row


class ClientRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_by_id(self, client_id: int) -> Client | None:
        return await self.session.get(Client, client_id)

    async def get_by_code(self, depositor_id: int, code: str) -> Client | None:
        if not code:
            return None
        stmt = select(Client).where(
            Client.depositor_id == depositor_id,
            Client.code == code,
        )
        return await self.session.scalar(stmt)

    async def list_by_depositor(self, depositor_id: int) -> list[Client]:
        stmt = select(Client).where(
            Client.depositor_id == depositor_id,
        )
        return list(await self.session.scalars(stmt))

    async def list_all(self) -> list[Client]:
        stmt = select(Client).where()
        return list(await self.session.scalars(stmt))

    async def insert(self, **kwargs) -> Client:
        row = Client(**kwargs)
        self.session.add(row)
        await self.session.flush()
        return row

    async def update(self, client_id: int, **kwargs) -> Client | None:
        row = await self.session.get(Client, client_id)
        if row is None:
            return None
        for field, value in kwargs.items():
            setattr(row, field, value)
        await self.session.flush()
        return row



class ContractRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_by_id(self, contract_id: int) -> Contract | None:
        return await self.session.get(Contract, contract_id)

    async def list_active(self) -> list[Contract]:
        stmt = select(Contract).where(
            Contract.status == "active",
        )
        return list(await self.session.scalars(stmt))

    async def list_all(self) -> list[Contract]:
        stmt = select(Contract).where()
        return list(await self.session.scalars(stmt))

    async def insert(self, **kwargs) -> Contract:
        row = Contract(**kwargs)
        self.session.add(row)
        await self.session.flush()
        return row

    async def update(self, contract_id: int, **kwargs) -> Contract | None:
        row = await self.session.get(Contract, contract_id)
        if row is None:
            return None
        for field, value in kwargs.items():
            setattr(row, field, value)
        await self.session.flush()
        return row


class TariffRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_document_by_id(self, document_id: int) -> TariffDocument | None:
        return await self.session.get(TariffDocument, document_id)

    async def insert_document(self, **kwargs) -> TariffDocument:
        row = TariffDocument(**kwargs)
        self.session.add(row)
        await self.session.flush()
        return row

    async def insert_tariff(self, **kwargs) -> Tariff:
        row = Tariff(**kwargs)
        self.session.add(row)
        await self.session.flush()
        return row

    async def list_tariffs_by_document(self, document_id: int) -> list[Tariff]:
        stmt = select(Tariff).where(
            Tariff.document_id == document_id,
        )
        return list(await self.session.scalars(stmt))


class DepositorRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_by_id(self, depositor_id: int) -> Depositor | None:
        return await self.session.get(Depositor, depositor_id)

    async def get_by_code(self, code: str) -> Depositor | None:
        if not code:
            return None
        stmt = select(Depositor).where(
            Depositor.code == code)
        return await self.session.scalar(stmt)

    async def list_all(self) -> list[Depositor]:
        stmt = select(Depositor).where()
        return list(await self.session.scalars(stmt))

    async def insert(self, **kwargs) -> Depositor:
        row = Depositor(**kwargs)
        self.session.add(row)
        await self.session.flush()
        return row
