"""Схемы модуля integration."""

from app.api.v1.integration.schemas.logs import IntegrationLogRead
from app.api.v1.integration.schemas.profiles import IntegrationProfileCreate, IntegrationProfileRead

__all__ = [
    "IntegrationLogRead",
    "IntegrationProfileRead",
    "IntegrationProfileCreate",
]
