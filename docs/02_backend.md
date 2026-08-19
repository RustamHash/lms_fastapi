# Бэкенд — структура и модули

## Структура модуля

app/{module}/
├── models/ # ORM-модели SQLAlchemy
│ └── init.py # экспорт всех моделей
├── services/ # бизнес-логика
│ └── init.py # экспорт сервисов
└── repository.py # SQL-запросы

## Модуль accounts

app/accounts/
├── models/
│ ├── user.py # User — пользователь
│ ├── role.py # Role — роли, M2M через user_roles
│ ├── audit.py # Audit — журнал действий
│ ├── user_settings.py # UserSettings — настройки UI
│ ├── user_table_settings.py # UserTableSettings — настройки таблиц
│ ├── user_depositor.py # UserDepositor — привязка к поклажедателю
│ └── user_trade_point.py # UserTradePoint — привязка к ТТ
├── services/
│ ├── user_service.py # создание, аутентификация, JWT
│ ├── role_service.py # роли и права
│ ├── audit_service.py # запись аудита
│ └── table_settings_service.py # настройки таблиц
└── repository.py # UserRepository, RoleRepository, AuditRepository, etc.

## Модуль parties

app/parties/
├── models/
│ ├── address.py # Address, RawAddress, DeliveryZone
│ ├── legal_entity.py # LegalEntity — юрлицо
│ ├── counterparty.py # Depositor, Keeper, Carrier
│ ├── client.py # Client, TradePoint
│ ├── contract.py # Contract
│ └── tariff.py # TariffDocument, Tariff
├── services/
│ ├── address_service.py # создание адресов, DaData, hash
│ ├── legal_entity_service.py
│ ├── client_service.py # ClientService + TradePointService
│ ├── contract_service.py
│ ├── tariff_service.py
│ └── depositor_service.py
└── repository.py # AddressRepository, LegalEntityRepository, etc.

## Модуль warehouse

app/warehouse/
├── models/
│ ├── topology.py # Warehouse, VirtualWarehouse, Zone, Row, Location
│ ├── product.py # ProductGroup, Product
│ ├── package.py # Package — упаковка
│ ├── batch.py # Batch — партия
│ ├── lpn.py # LPN — паллета
│ ├── stock_balance.py # StockBalance — остатки
│ ├── stock_movement.py # StockMovement — движения
│ ├── task.py # Task, TaskLine — задания
│ └── product_location.py # ProductLocation — товар-ячейка
├── services/
│ ├── stock_service.py # приход, расход, перемещение, резерв
│ ├── batch_service.py # партии
│ ├── lpn_service.py # паллеты
│ ├── placement_service.py # FEFO размещение
│ ├── product_service.py # товары
│ └── task_service.py # задания с фактом
└── repository.py

## Модуль documents

app/documents/
├── models/
│ └── document.py # Document, DocumentLine
├── services/
│ └── document_service.py # создание, статусы, строки
└── repository.py

## Модуль delivery

app/delivery/
├── models/
│ ├── delivery_order.py # DeliveryOrder, DeliveryDeviation
│ ├── driver.py # Driver, Vehicle
│ └── route.py # Route, RouteLine
├── services/
│ └── delivery_order_service.py # статусы, создание
└── repository.py

## Модуль integration

app/integration/
├── models/
│ └── integration_profile.py # IntegrationProfile, IntegrationLog, IntegrationError
├── services/
│ ├── ftp_service.py # FTP-клиент
│ └── integration_service.py # IntegrationService + AdapterService
├── adapters/
│ ├── base.py # BaseAdapter
│ └── zln_adapter.py # ZLNAdapter — парсинг XML
└── repository.py

## Модуль notifications

app/notifications/
├── models/
│ └── notification.py
├── services/
│ └── notification_service.py
└── repository.py

## Инфраструктура

app/infrastructure/
├── orm_base.py # Base — базовый класс с audit-полями
├── uow.py # UnitOfWork — транзакции
├── audit/
│ ├── events.py
│ └── service.py
├── files/
│ └── models.py # File — файлы
├── logging/
│ └── setup.py # настройка логирования
└── external/
 └── dadata.py # DaDataClient — геокодинг

## Ядро

app/core/
├── config.py # Settings — из .env
├── database.py # async engine, session factory
├── dependencies.py # get_session, get_current_user, require_permission
├── security.py # JWT, bcrypt
└── middleware.py # не используется, можно удалить

## API

app/api/v1/
├── router.py # главный роутер
├── accounts/
│ ├── schemas.py # Pydantic-схемы
│ └── routes.py # auth, users, roles, table-settings
├── parties/
│ ├── schemas.py
│ └── routes.py # addresses, aliases, legal-entities, depositors, clients, trade-points, contracts, tariffs
├── warehouse/
│ ├── schemas.py
│ └── routes.py # products, batches, lpns, stock, tasks
├── documents/
│ ├── schemas.py
│ └── routes.py
├── delivery/
│ ├── schemas.py
│ └── routes.py
├── integration/
│ ├── schemas.py
│ └── routes.py
├── notifications/
│ ├── schemas.py
│ └── routes.py
└── files/
 ├── schemas.py
 └── routes.py
