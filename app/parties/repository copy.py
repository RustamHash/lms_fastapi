# app/parties/repository.py

"""Репозитории для модуля parties."""

from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

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
        self._s = session

    async def get_by_id(self, id: int) -> Address | None:
        stmt = (
            select(Address)
            .where(Address.id == id)
            .options(selectinload(Address.delivery_zone))
        )
        return await self._s.scalar(stmt)

    async def list_all(self) -> list[Address]:
        stmt = select(Address).options(selectinload(Address.delivery_zone))
        return list(await self._s.scalars(stmt))

    async def create(self, **kwargs) -> Address:
        row = Address(**kwargs)
        self._s.add(row)
        await self._s.flush()
        # Перезагружаем с delivery_zone
        if row.delivery_zone_id:
            await self._s.refresh(row, attribute_names=["delivery_zone"])
        return row

    async def update(self, id: int, **kwargs) -> Address | None:
        row = await self.get_by_id(id)
        if row is None:
            return None
        for field, value in kwargs.items():
            setattr(row, field, value)
        await self._s.flush()
        # Перезагружаем с обновленной delivery_zone
        if "delivery_zone_id" in kwargs:
            await self._s.refresh(row, attribute_names=["delivery_zone"])
        return row

    async def soft_delete(self, id: int, user_id: int | None = None) -> bool:
        row = await self.get_by_id(id)
        if row is None:
            return False
        row.soft_delete(user_id)
        await self._s.flush()
        return True


class RawAddressRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._s = session

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

    async def create(self, **kwargs) -> RawAddress:
        row = RawAddress(**kwargs)
        self._s.add(row)
        await self._s.flush()
        return row

    async def update(self, id: int, **kwargs) -> RawAddress | None:
        row = await self.get_by_id(id)
        if row is None:
            return None
        for field, value in kwargs.items():
            setattr(row, field, value)
        await self._s.flush()
        return row

    async def soft_delete(self, id: int, user_id: int | None = None) -> bool:
        row = await self.get_by_id(id)
        if row is None:
            return False
        row.soft_delete(user_id)
        await self._s.flush()
        return True


class LegalEntityRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._s = session

    async def get_by_id(self, id: int) -> LegalEntity | None:
        stmt = (
            select(LegalEntity)
            .where(LegalEntity.id == id)
            .options(
                selectinload(LegalEntity.legal_address),
                selectinload(LegalEntity.actual_address),
            )
        )
        return await self._s.scalar(stmt)

    async def list_all(self) -> list[LegalEntity]:
        stmt = select(LegalEntity).options(
            selectinload(LegalEntity.legal_address),
            selectinload(LegalEntity.actual_address),
        )
        return list(await self._s.scalars(stmt))

    async def create(self, **kwargs) -> LegalEntity:
        row = LegalEntity(**kwargs)
        self._s.add(row)
        await self._s.flush()
        return row

    async def update(self, id: int, **kwargs) -> LegalEntity | None:
        row = await self.get_by_id(id)
        if row is None:
            return None
        for field, value in kwargs.items():
            setattr(row, field, value)
        await self._s.flush()
        return row

    async def soft_delete(self, id: int, user_id: int | None = None) -> bool:
        row = await self.get_by_id(id)
        if row is None:
            return False
        row.soft_delete(user_id)
        await self._s.flush()
        return True


class ClientRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._s = session

    async def get_by_id(self, id: int) -> Client | None:
        stmt = (
            select(Client)
            .where(Client.id == id)
            .options(
                selectinload(Client.depositor),
                selectinload(Client.legal_address),
                selectinload(Client.delivery_address),
            )
        )
        return await self._s.scalar(stmt)

    async def list_all(self) -> list[Client]:
        stmt = select(Client).options(
            selectinload(Client.depositor),
            selectinload(Client.legal_address),
            selectinload(Client.delivery_address),
        )
        return list(await self._s.scalars(stmt))

    async def create(self, **kwargs) -> Client:
        row = Client(**kwargs)
        self._s.add(row)
        await self._s.flush()
        return row

    async def update(self, id: int, **kwargs) -> Client | None:
        row = await self.get_by_id(id)
        if row is None:
            return None
        for field, value in kwargs.items():
            setattr(row, field, value)
        await self._s.flush()
        return row

    async def soft_delete(self, id: int, user_id: int | None = None) -> bool:
        row = await self.get_by_id(id)
        if row is None:
            return False
        row.soft_delete(user_id)
        await self._s.flush()
        return True


class DepositorRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._s = session

    async def get_by_id(self, id: int) -> Depositor | None:
        stmt = (
            select(Depositor)
            .where(Depositor.id == id)
            .options(selectinload(Depositor.legal_entity))
        )
        return await self._s.scalar(stmt)

    async def list_all(self) -> list[Depositor]:
        stmt = select(Depositor).options(selectinload(Depositor.legal_entity))
        return list(await self._s.scalars(stmt))

    async def create(self, **kwargs) -> Depositor:
        row = Depositor(**kwargs)
        self._s.add(row)
        await self._s.flush()
        return row

    async def update(self, id: int, **kwargs) -> Depositor | None:
        row = await self.get_by_id(id)
        if row is None:
            return None
        for field, value in kwargs.items():
            setattr(row, field, value)
        await self._s.flush()
        return row

    async def soft_delete(self, id: int, user_id: int | None = None) -> bool:
        row = await self.get_by_id(id)
        if row is None:
            return False
        row.soft_delete(user_id)
        await self._s.flush()
        return True


class ContractRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._s = session

    async def get_by_id(self, id: int) -> Contract | None:
        stmt = (
            select(Contract)
            .where(Contract.id == id)
            .options(
                selectinload(Contract.customer),
                selectinload(Contract.executor),
                selectinload(Contract.tariff_documents),
            )
        )
        return await self._s.scalar(stmt)

    async def list_all(self) -> list[Contract]:
        stmt = select(Contract).options(
            selectinload(Contract.customer), selectinload(Contract.executor)
        )
        return list(await self._s.scalars(stmt))

    async def create(self, **kwargs) -> Contract:
        row = Contract(**kwargs)
        self._s.add(row)
        await self._s.flush()
        return row

    async def update(self, id: int, **kwargs) -> Contract | None:
        row = await self.get_by_id(id)
        if row is None:
            return None
        for field, value in kwargs.items():
            setattr(row, field, value)
        await self._s.flush()
        return row

    async def soft_delete(self, id: int, user_id: int | None = None) -> bool:
        row = await self.get_by_id(id)
        if row is None:
            return False
        row.soft_delete(user_id)
        await self._s.flush()
        return True


class TariffDocumentRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._s = session

    async def get_by_id(self, id: int) -> TariffDocument | None:
        stmt = (
            select(TariffDocument)
            .where(TariffDocument.id == id)
            .options(
                selectinload(TariffDocument.contract),
                selectinload(TariffDocument.tariffs),
            )
        )
        return await self._s.scalar(stmt)

    async def list_all(self) -> list[TariffDocument]:
        stmt = select(TariffDocument).options(selectinload(TariffDocument.contract))
        return list(await self._s.scalars(stmt))

    async def create(self, **kwargs) -> TariffDocument:
        row = TariffDocument(**kwargs)
        self._s.add(row)
        await self._s.flush()
        return row

    async def update(self, id: int, **kwargs) -> TariffDocument | None:
        row = await self.get_by_id(id)
        if row is None:
            return None
        for field, value in kwargs.items():
            setattr(row, field, value)
        await self._s.flush()
        return row

    async def soft_delete(self, id: int, user_id: int | None = None) -> bool:
        row = await self.get_by_id(id)
        if row is None:
            return False
        row.soft_delete(user_id)
        await self._s.flush()
        return True


class TariffRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._s = session

    async def get_by_id(self, id: int) -> Tariff | None:
        stmt = (
            select(Tariff).where(Tariff.id == id).options(selectinload(Tariff.document))
        )
        return await self._s.scalar(stmt)

    async def list_all(self) -> list[Tariff]:
        stmt = select(Tariff).options(selectinload(Tariff.document))
        return list(await self._s.scalars(stmt))

    async def create(self, **kwargs) -> Tariff:
        row = Tariff(**kwargs)
        self._s.add(row)
        await self._s.flush()
        return row

    async def update(self, id: int, **kwargs) -> Tariff | None:
        row = await self.get_by_id(id)
        if row is None:
            return None
        for field, value in kwargs.items():
            setattr(row, field, value)
        await self._s.flush()
        return row

    async def soft_delete(self, id: int, user_id: int | None = None) -> bool:
        row = await self.get_by_id(id)
        if row is None:
            return False
        row.soft_delete(user_id)
        await self._s.flush()
        return True


class DeliveryZoneRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._s = session

    async def get_by_id(self, id: int) -> DeliveryZone | None:
        return await self._s.get(DeliveryZone, id)

    async def list_all(self) -> list[DeliveryZone]:
        stmt = select(DeliveryZone)
        return list(await self._s.scalars(stmt))

    async def create(self, **kwargs) -> DeliveryZone:
        row = DeliveryZone(**kwargs)
        self._s.add(row)
        await self._s.flush()
        return row

    async def update(self, id: int, **kwargs) -> DeliveryZone | None:
        row = await self.get_by_id(id)
        if row is None:
            return None
        for field, value in kwargs.items():
            setattr(row, field, value)
        await self._s.flush()
        return row

    async def soft_delete(self, id: int, user_id: int | None = None) -> bool:
        row = await self.get_by_id(id)
        if row is None:
            return False
        row.soft_delete(user_id)
        await self._s.flush()
        return True


class CarrierRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._s = session

    async def get_by_id(self, id: int) -> Carrier | None:
        stmt = (
            select(Carrier)
            .where(Carrier.id == id)
            .options(selectinload(Carrier.legal_entity))
        )
        return await self._s.scalar(stmt)

    async def list_all(self) -> list[Carrier]:
        stmt = select(Carrier).options(selectinload(Carrier.legal_entity))
        return list(await self._s.scalars(stmt))

    async def create(self, **kwargs) -> Carrier:
        row = Carrier(**kwargs)
        self._s.add(row)
        await self._s.flush()
        return row

    async def update(self, id: int, **kwargs) -> Carrier | None:
        row = await self.get_by_id(id)
        if row is None:
            return None
        for field, value in kwargs.items():
            setattr(row, field, value)
        await self._s.flush()
        return row

    async def soft_delete(self, id: int, user_id: int | None = None) -> bool:
        row = await self.get_by_id(id)
        if row is None:
            return False
        row.soft_delete(user_id)
        await self._s.flush()
        return True


class KeeperRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._s = session

    async def get_by_id(self, id: int) -> Keeper | None:
        stmt = (
            select(Keeper)
            .where(Keeper.id == id)
            .options(selectinload(Keeper.legal_entity))
        )
        return await self._s.scalar(stmt)

    async def list_all(self) -> list[Keeper]:
        stmt = select(Keeper).options(selectinload(Keeper.legal_entity))
        return list(await self._s.scalars(stmt))

    async def create(self, **kwargs) -> Keeper:
        row = Keeper(**kwargs)
        self._s.add(row)
        await self._s.flush()
        return row

    async def update(self, id: int, **kwargs) -> Keeper | None:
        row = await self.get_by_id(id)
        if row is None:
            return None
        for field, value in kwargs.items():
            setattr(row, field, value)
        await self._s.flush()
        return row

    async def soft_delete(self, id: int, user_id: int | None = None) -> bool:
        row = await self.get_by_id(id)
        if row is None:
            return False
        row.soft_delete(user_id)
        await self._s.flush()
        return True
