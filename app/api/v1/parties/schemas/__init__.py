"""Схемы модуля parties."""

from app.api.v1.parties.schemas.addresses import (
    DeliveryZoneRead,
    DeliveryZoneUpdate,
    DeliveryZoneCreate,
    AddressRead,
    AddressCreate,
    AddressResolve,
    AddressUpdate,
)
from app.api.v1.parties.schemas.legal_entities import (
    LegalEntityRead,
    LegalEntityCreate,
    LegalEntityUpdate,
)
from app.api.v1.parties.schemas.counterparties import (
    CarrierRead,
    CarrierUpdate,
    CarrierCreate,
    KeeperRead,
    KeeperUpdate,
    KeeperCreate,
    DepositorRead,
    DepositorCreate,
    DepositorUpdate,
)
from app.api.v1.parties.schemas.clients import (
    ClientRead,
    ClientCreate,
    ClientUpdate,
)
from app.api.v1.parties.schemas.contracts import (
    ContractRead,
    ContractCreate,
    ContractUpdate,
)
from app.api.v1.parties.schemas.tariffs import (
    TariffDocumentRead,
    TariffDocumentCreate,
    TariffDocumentUpdate,
    TariffRead,
    TariffCreate,
    TariffUpdate,
)
from app.api.v1.parties.schemas.raw_addresses import (
    AliasCreate,
    AliasUpdate,
    RawAddressCreate,
    RawAddressUpdate,
    RawAddressRead,
)

__all__ = [
    # Addresses
    "DeliveryZoneRead",
    "DeliveryZoneUpdate",
    "DeliveryZoneCreate",
    "AddressRead",
    "AddressCreate",
    "AddressResolve",
    "AddressUpdate",
    # Legal Entities
    "LegalEntityRead",
    "LegalEntityCreate",
    "LegalEntityUpdate",
    # Counterparties
    "CarrierRead",
    "CarrierUpdate",
    "CarrierCreate",
    "KeeperRead",
    "KeeperUpdate",
    "KeeperCreate",
    "DepositorRead",
    "DepositorCreate",
    "DepositorUpdate",
    # Clients
    "ClientRead",
    "ClientCreate",
    "ClientUpdate",
    # Contracts
    "ContractRead",
    "ContractCreate",
    "ContractUpdate",
    # Tariffs
    "TariffDocumentRead",
    "TariffDocumentCreate",
    "TariffDocumentUpdate",
    "TariffRead",
    "TariffCreate",
    "TariffUpdate",
    # Raw Addresses
    "AliasCreate",
    "AliasUpdate",
    "RawAddressCreate",
    "RawAddressUpdate",
    "RawAddressRead",
]

# Пересобираем схемы для разрешения циклических ссылок
DeliveryZoneRead.model_rebuild()
AddressRead.model_rebuild()
LegalEntityRead.model_rebuild()
CarrierRead.model_rebuild()
KeeperRead.model_rebuild()
DepositorRead.model_rebuild()
ClientRead.model_rebuild()
ContractRead.model_rebuild()
TariffDocumentRead.model_rebuild()
TariffRead.model_rebuild()
RawAddressRead.model_rebuild()
