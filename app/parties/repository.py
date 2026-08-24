# app/parties/repository.py

"""Репозитории для модуля parties."""

from __future__ import annotations


from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.infrastructure.repo_base import BaseRepository
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


class RawAddressRepository(BaseRepository[RawAddress]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, RawAddress)


class LegalEntityRepository(BaseRepository[LegalEntity]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, LegalEntity)


class ClientRepository(BaseRepository[Client]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, Client)


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
