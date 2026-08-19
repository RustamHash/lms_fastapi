"""Сервисы модуля parties."""

from app.parties.services.address_service import AddressService
from app.parties.services.legal_entity_service import LegalEntityService
from app.parties.services.client_service import ClientService, TradePointService
from app.parties.services.contract_service import ContractService
from app.parties.services.tariff_service import TariffService
from app.parties.services.depositor_service import DepositorService

__all__ = [
    "AddressService",
    "LegalEntityService",
    "ClientService",
    "TradePointService",
    "ContractService",
    "TariffService",
    "DepositorService",
]
