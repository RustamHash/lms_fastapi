# app/api/deps.py

"""Общие зависимости для API."""

from __future__ import annotations

from typing import Annotated

from fastapi import Depends, HTTPException, Request, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.accounts.models import User
from app.accounts.repository import UserRepository
from app.accounts.scope import DataScope
from app.core.database import async_session_factory
from app.core.exceptions import ForbiddenError
from app.core.security import decode_token_sub_user_id
from app.infrastructure.uow import UnitOfWork

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/token", auto_error=False)


# ========== Базовые зависимости ==========


async def get_session(request: Request):
    """Сессия с автоматическим commit/rollback."""
    async with UnitOfWork(async_session_factory) as session:
        request.state.session = session
        yield session


async def get_current_user_id(token: str | None = Depends(oauth2_scheme)) -> int | None:
    """ID текущего пользователя (None, если не авторизован)."""
    if not token:
        return None
    try:
        return decode_token_sub_user_id(token)
    except ValueError:
        return None


async def get_current_user(
    session: AsyncSession = Depends(get_session),
    token: str | None = Depends(oauth2_scheme),
) -> User:
    """Текущий пользователь (объект User, требует авторизации)."""
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Не авторизован"
        )
    try:
        user_id = decode_token_sub_user_id(token)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Недействительный токен"
        ) from None
    repo = UserRepository(session)
    user = await repo.get_by_id(user_id)
    if user is None or user.is_deleted or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Пользователь не найден или деактивирован",
        )
    return user


# ========== Аннотированные зависимости ==========

SessionDep = Annotated[AsyncSession, Depends(get_session)]
UserDep = Annotated[int | None, Depends(get_current_user_id)]
CurrentUser = Annotated[User, Depends(get_current_user)]


async def get_data_scope(
    user: CurrentUser,
    session: AsyncSession = Depends(get_session),
) -> DataScope:
    full = await UserRepository(session).get_by_id(user.id, with_depositors=True)
    if full is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Пользователь не найден или деактивирован",
        )
    from app.accounts.scope import build_scope

    return build_scope(full)


ScopeDep = Annotated[DataScope, Depends(get_data_scope)]


# ========== Проверка прав ==========


def require_permission(action: str, entity: str):
    async def checker(current_user: CurrentUser) -> User:
        if not current_user.has_permission(action, entity):
            raise ForbiddenError(f"Нет права: {action}:{entity}")
        return current_user

    return checker


def require_group(entity: str):
    async def checker(current_user: CurrentUser) -> User:
        if not current_user.has_group_access(entity):
            raise ForbiddenError(f"Нет доступа к модулю: {entity}")
        return current_user

    return checker


# ========== Контейнер сервисов ==========


class ServiceContainer:
    """Контейнер всех сервисов приложения."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

        # ===== Accounts =====
        from app.accounts.repository import (
            RoleRepository,
            UserClientRepository,
            UserDepositorRepository,
            UserRepository,
        )
        from app.accounts.services.role_service import RoleService
        from app.accounts.services.user_service import UserService

        user_repo = UserRepository(session)
        role_repo = RoleRepository(session)
        self.user = UserService(
            user_repo,
            role_repo,
            UserDepositorRepository(session),
            UserClientRepository(session),
        )
        self.role = RoleService(role_repo)

        # ===== Parties =====
        from app.parties.repository import (
            AddressRepository,
            CarrierRepository,
            ClientRepository,
            ContractRepository,
            DeliveryZoneRepository,
            DepositorRepository,
            KeeperRepository,
            LegalEntityRepository,
            RawAddressRepository,
            TariffDocumentRepository,
            TariffRepository,
        )
        from app.parties.services.address_service import AddressService
        from app.parties.services.carrier_service import CarrierService
        from app.parties.services.client_service import ClientService
        from app.parties.services.contract_service import ContractService
        from app.parties.services.delivery_zone_service import DeliveryZoneService
        from app.parties.services.depositor_service import DepositorService
        from app.parties.services.keeper_service import KeeperService
        from app.parties.services.legal_entity_service import LegalEntityService
        from app.parties.services.raw_address_service import RawAddressService
        from app.parties.services.tariff_document_service import TariffDocumentService
        from app.parties.services.tariff_service import TariffService

        self.address = AddressService(
            AddressRepository(session), RawAddressRepository(session)
        )
        self.carrier = CarrierService(CarrierRepository(session))
        self.client = ClientService(ClientRepository(session))
        self.contract = ContractService(ContractRepository(session))
        self.delivery_zone = DeliveryZoneService(DeliveryZoneRepository(session))
        self.depositor = DepositorService(DepositorRepository(session))
        self.keeper = KeeperService(KeeperRepository(session))
        self.legal_entity = LegalEntityService(LegalEntityRepository(session))
        self.raw_address = RawAddressService(
            RawAddressRepository(session), self.address
        )
        self.tariff = TariffService(TariffRepository(session))
        self.tariff_document = TariffDocumentService(TariffDocumentRepository(session))

        # ===== Warehouse =====
        from app.warehouse.repository import (
            BatchRepository,
            LPNRepository,
            ProductRepository,
            StockRepository,
            TaskLineRepository,
            TaskRepository,
        )
        from app.warehouse.services.batch_service import BatchService
        from app.warehouse.services.lpn_service import LPNService
        from app.warehouse.services.product_service import ProductService
        from app.warehouse.services.stock_service import StockService
        from app.warehouse.services.task_service import TaskService

        self.product = ProductService(ProductRepository(session))
        self.batch = BatchService(BatchRepository(session))
        self.lpn = LPNService(LPNRepository(session))
        self.stock = StockService(StockRepository(session))
        self.task = TaskService(
            TaskRepository(session),
            TaskLineRepository(session),
            StockService(StockRepository(session)),
        )

        # ===== Orders =====
        from app.orders.repository import (
            InboundOrderLineRepository,
            InboundOrderRepository,
            OutboundOrderLineRepository,
            OutboundOrderRepository,
            ReturnOrderLineRepository,
            ReturnOrderRepository,
        )
        from app.orders.services.inbound_order_service import InboundOrderService
        from app.orders.services.outbound_order_service import OutboundOrderService
        from app.orders.services.return_order_service import ReturnOrderService

        self.inbound_order = InboundOrderService(
            InboundOrderRepository(session),
            InboundOrderLineRepository(session),
        )
        self.outbound_order = OutboundOrderService(
            OutboundOrderRepository(session),
            OutboundOrderLineRepository(session),
        )
        self.return_order = ReturnOrderService(
            ReturnOrderRepository(session),
            ReturnOrderLineRepository(session),
        )

        # ===== Delivery =====
        from app.delivery.repository import (
            DeliveryOrderRepository,
            DeviationRepository,
            DriverRepository,
            RouteLineRepository,
            RouteRepository,
            VehicleRepository,
        )
        from app.delivery.services.delivery_order_service import DeliveryOrderService
        from app.delivery.services.driver_service import DriverService
        from app.delivery.services.vehicle_service import VehicleService
        from app.delivery.services.route_service import RouteService
        from app.delivery.services.route_line_service import RouteLineService
        from app.delivery.services.deviation_service import DeviationService

        self.delivery_order = DeliveryOrderService(DeliveryOrderRepository(session))
        self.driver = DriverService(DriverRepository(session))
        self.vehicle = VehicleService(VehicleRepository(session))
        self.route = RouteService(RouteRepository(session))
        self.route_line = RouteLineService(RouteLineRepository(session))
        self.deviation = DeviationService(DeviationRepository(session))

        # ===== Documents =====
        from app.documents.repository import DocumentLineRepository, DocumentRepository
        from app.documents.services.document_service import DocumentService

        self.document = DocumentService(
            DocumentRepository(session),
            DocumentLineRepository(session),
        )

        # ===== Notifications =====
        from app.notifications.repository import (
            NotificationRepository,
            NotificationRuleRepository,
        )
        from app.notifications.services.notification_service import NotificationService

        self.notification = NotificationService(NotificationRepository(session))
        self.notification_rule_repo = NotificationRuleRepository(session)

        # ===== Files =====
        from app.files.repository import FileRepository
        from app.files.services.file_service import FileService

        self.file = FileService(FileRepository(session))


async def get_services(
    session: AsyncSession = Depends(get_session),
) -> ServiceContainer:
    """Фабрика контейнера сервисов."""
    return ServiceContainer(session)


Services = Annotated[ServiceContainer, Depends(get_services)]
