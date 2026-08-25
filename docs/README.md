# Документация LMS FastAPI

Монолит склада / 3PL: FastAPI + SQLAlchemy async + PostgreSQL, UI в `frontend/`.
Код организован **по фичам**, не по слоям. Слои живут внутри фичи.

```
HTTP → Router → Service → Repository → PostgreSQL
                 │
                 └── event_bus → notifications / другие подписчики
```

---

## Как пользоваться этой папкой

| Файл | Что внутри |
|------|------------|
| Этот файл | Карта проекта, запуск, ссылки на модули |
| [modules/…](modules/) | Деталка по каждой фиче: модели, сервисы, API, связи |
| [../ARCHITECTURE.md](../ARCHITECTURE.md) | Слои, DI, транзакции — **источник истины по устройству кода** |
| [09_models_improvements.md](09_models_improvements.md) | Долг по ORM-моделям |
| [../plans/rewrite-phases.md](../plans/rewrite-phases.md) | Спека догонки до WMS_01 |
| [../plans/STATUS.md](../plans/STATUS.md) | Очередь работ для чатов |

Правило для агентов: при изменении кода обновлять соответствующую деталку и эту карту, если появился новый модуль, префикс API или сущность. См. `.cursor/rules/docs.mdc`.

---

## Стек

| Слой | Технологии |
|------|------------|
| API | FastAPI, Pydantic, JWT |
| БД | PostgreSQL 16, SQLAlchemy 2 async, Alembic |
| Фон | Celery + Redis (импорт) |
| UI | React 19, Vite, React Router 7, TanStack Query |
| Внешнее | DaData (адреса), FTP (интеграции) |

Точка входа API: `app/main.py`. Сборка роутов: `app/api/v1/router.py`, префикс `/api/v1`.
Swagger: `/docs`. OpenAPI: `/openapi.json`.

---

## Запуск

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # заполнить DATABASE_URL, JWT_SECRET_KEY
alembic upgrade head
uvicorn app.main:app --reload --host 0.0.0.0 --port 8080
```

Docker (dev): `docker compose -f docker-compose.dev.yml up` — Postgres, Redis, FastAPI (`:8080`), Celery, frontend.

Скрипты:

- `scripts/create_superuser.py admin password`
- `scripts/create_default_roles.py`
- `scripts/clear_orders.py`

Фронт в dev: Vite на `:5173` (CORS уже в настройках). В prod собранный `frontend/dist` раздаётся из FastAPI.

Тесты склада: `pytest tests/warehouse` (нужен PostgreSQL; БД `lms_fastapi_test` создаётся сама).

---

## Карта модулей

Каждая фича: `app/{feature}/` (модели, сервисы, репозиторий) + `app/api/v1/{feature}/` (роуты, схемы, deps). Исключение: `files` — вертикальный срез в одном пакете.

| Модуль | Назначение | Код | API (после `/api/v1`) | Деталка |
|--------|------------|-----|----------------------|---------|
| **accounts** | Пользователи, роли, RBAC, скоуп поклажедатель/клиент, аудит, настройки списков | `app/accounts/` | `/auth`, `/users`, `/roles`, `/permissions/available`, `/audit`, `/table-settings`, `/list-presets` | [accounts.md](modules/accounts.md) |
| **parties** | Контрагенты 3PL: юрлица, поклажедатели, клиенты, адреса, договоры, тарифы | `app/parties/` | `/addresses`, `/aliases`, `/legal-entities`, `/depositors`, `/clients`, `/contracts`, `/tariffs`, `/tariff-documents`, `/delivery-zones`, `/carriers`, `/keepers` | [parties.md](modules/parties.md) |
| **warehouse** | Топология, товары, партии, LPN, остатки, приёмка/отбор | `app/warehouse/` | `/warehouse/...`, `/warehouse/receiving`, `/warehouse/picking`, `/warehouse/topology/...` | [warehouse.md](modules/warehouse.md) |
| **orders** | Входящие / исходящие / возвраты | `app/orders/` | `/inbound-orders`, `/outbound-orders`, `/return-orders` | [orders.md](modules/orders.md) |
| **documents** | Складские документы и строки | `app/documents/` | `/documents` | [documents.md](modules/documents.md) |
| **delivery** | Заявки на доставку, водители, ТС, маршруты, отклонения | `app/delivery/` | `/delivery/...` | [delivery.md](modules/delivery.md) |
| **notifications** | In-app / email по правилам и событиям | `app/notifications/` | `/notifications`, `/notification-rules` | [notifications.md](modules/notifications.md) |
| **integration** | FTP, адаптер XML, журнал; заказ создаёт orders | `app/integration/` | `/integrations` | [integration.md](modules/integration.md) |
| **files** | Загрузка и выдача файлов | `app/files/` | `/files` | [files.md](modules/files.md) |
| **core** | Конфиг, JWT, исключения, middleware, статусы | `app/core/` | — | [core.md](modules/core.md) |
| **infrastructure** | ORM Base, репозиторий, UoW, события, DaData, логи | `app/infrastructure/` | — | [infrastructure.md](modules/infrastructure.md) |
| **frontend** | SPA: списки сущностей, хабы, auth | `frontend/` | — | [frontend.md](modules/frontend.md) |
| **api** | Сборка `/api/v1`, общие Depends, метаданные полей для UI | `app/api/` | `/entities` | [api.md](modules/api.md) |

---

## Слои внутри фичи (кратко)

Подробно: [ARCHITECTURE.md](../ARCHITECTURE.md).

- **Router** — HTTP, схемы, `Depends(get_*_service)`, `require_permission`. Без SQL и бизнес-правил.
- **Service** — инварианты, оркестрация, `event_bus.emit`. Ошибки: `NotFoundError` / `BadRequestError` / `ConflictError`.
- **Repository** — доступ к данным. Наследует `BaseRepository`.

Фабрики сервисов — рядом с роутами домена (`app/api/v1/{feature}/deps.py`), не все в `app/api/deps.py`. Сейчас так сделан склад; остальные фичи ещё частично на `ServiceContainer` (этап 7).

---

## RBAC и скоуп данных

Права: `require_permission(action, entity)`. Каталог сущностей и действий — `app/accounts/permissions_catalog.py`.

Скоуп (`app/accounts/scope.py`):

- нет привязок к поклажедателям → сотрудник склада, видит всё;
- только поклажедатели → менеджер поклажедателя;
- поклажедатели + клиенты → торговый агент.

Скоуп на списках: клиенты, inbound/outbound/return, заявки на доставку (list/get/patch/delete). Товары, поклажедатели и создание заявки на доставку — пока без фильтра.

---

## Потоки данных (как задумано)

```
Поклажедатель (FTP/XML)
        │
        ▼
  integration  ──сообщение──►  InboundExchangeService (orders)
        │                              │
        │                              ├─► warehouse receiving / picking ─► stock
        │                              │
        │                              ▼
        │                         documents (receipt с inbound_order_id)
        │
outbound + needs_delivery ──► delivery order ──► route
```

Задание приёмки/отбора создаётся из заказа (`ReceivingService` / `PickingService`), не руками через generic Task CRUD. TSD API — этап 5. XML-ответ партнёру — этап 4.

---

## Таблицы БД по модулям

Префикс имени таблицы ≈ модуль: `accounts_*`, `parties_*`, `warehouse_*`, `orders_*`, `documents_*`, `delivery_*`, `notifications_*`, `integration_*`, `files`.

Все ORM-модели наследуют `Base` (`id`, audit, soft delete). Известные проблемы этой модели — [09_models_improvements.md](09_models_improvements.md).
