# Архитектура LMS FastAPI

Карта модулей и API: [docs/README.md](docs/README.md).

Монолит склада / 3PL: FastAPI + SQLAlchemy async + PostgreSQL, фронт в `frontend/`.
Организация — **по фичам**, не по слоям. Слои живут *внутри* фичи.

```
HTTP → Router → Service → Repository → PostgreSQL
                 │
                 └── event_bus → notifications / другие подписчики
```

Отдельного пакета `app/domain/` нет и не планируется: домен — ORM-модели и сервисы фичи.

Поэтапная догонка до WMS_01: `plans/rewrite-phases.md`.
Очередь для чатов (кто что взял): `plans/STATUS.md`.

---

## Карта кода

```
app/
├── main.py                         # FastAPI app, exception handlers, startup
├── tasks.py                        # Celery
├── api/
│   ├── deps.py                     # сессия, auth, RBAC  (не фабрики сервисов)
│   └── v1/
│       ├── router.py               # сборка /api/v1
│       ├── base_schemas.py         # BaseRead
│       └── {feature}/
│           ├── routes/             # HTTP
│           ├── schemas/            # Pydantic
│           └── deps.py             # get_*_service  (целевое место)
├── {feature}/                      # accounts, parties, warehouse, orders,
│   ├── models/                     #   delivery, documents, notifications,
│   ├── services/                   #   integration
│   └── repository.py
├── files/                          # вертикальный срез: models + routes + schemas
├── core/                           # сквозные вещи приложения
└── infrastructure/                 # персистентность и тех. I/O
```

Фича не импортирует `repository` / `services` другой фичи. Связь между фичами — через сервис или событие, не через чужой SQL.

---

## Слои внутри фичи

### Router (`app/api/v1/{feature}/routes/`)

Делает:

- принимает HTTP, валидирует вход схемами;
- инжектит **один сервис** через `Depends(get_*_service)`;
- ставит `require_permission` на эндпоинт;
- мапит ORM → схема (`response_model` + `from_attributes`, либо явный `model_validate`);
- бросает `NotFoundError`, если сервис вернул `None`.

Не делает:

- SQL (`select`, `session.execute`, `session.add`);
- вызов репозитория;
- `XxxService(XxxRepository(session))` в хендлере;
- бизнес-правила (лимиты остатка, уникальность кода, переходы статуса).

CRUD-справочник без правил — тонкий сервис всё равно нужен. Роут не ходит в репозиторий «потому что логики нет».

```python
@router.get("", response_model=list[ClientRead],
            dependencies=[Depends(require_permission("view", "clients"))])
async def list_clients(
    service: ClientService = Depends(get_client_service),
) -> list[ClientRead]:
    rows = await service.list_all()
    return [ClientRead.model_validate(r) for r in rows]
```

### Service (`app/{feature}/services/`)

Делает:

- правила и инварианты;
- оркестрацию нескольких репозиториев / сервисов;
- `event_bus.emit(...)`.

Не делает:

- SQL напрямую (исключение — массовые `flush` внутри уже открытой сессии репозитория, это техдолг, не образец);
- FastAPI: `Depends`, `Request`, `JSONResponse`;
- commit/rollback — это UoW в `get_session`.

Ошибки: `NotFoundError` / `BadRequestError` / `ConflictError` из `app.core.exceptions`. Не `ValueError` — роут не должен угадывать, это 400 или 409.

Пустой прокси к репозиторию для справочника допустим. Не обязательно выдумывать «бизнес-логику».

```python
class ProductService:
    def __init__(self, repo: ProductRepository) -> None:
        self._repo = repo

    async def create(self, **kwargs) -> Product:
        existing = await self._repo.get_by_external_id(
            kwargs["depositor_id"], kwargs["external_id"]
        )
        if existing:
            raise ConflictError("Товар с таким кодом уже существует")
        return await self._repo.create(**kwargs)
```

### Repository (`app/{feature}/repository.py`)

Делает только доступ к данным. Наследует `BaseRepository`, переопределяет `get_by_id` / `list_all`, когда нужен `selectinload`. Специфичные методы — `get_by_username`, `get_balance`, `list_by_order`.

Не делает: правила, события, вызовы других репозиториев, HTTP.

```python
class ProductRepository(BaseRepository[Product]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, Product)

    async def get_by_id(self, id: int) -> Product | None:
        stmt = (
            select(Product)
            .where(Product.id == id)
            .options(selectinload(Product.group))
        )
        return await self._s.scalar(stmt)
```

`BaseRepository` (`app/infrastructure/repo_base.py`): `get_by_id`, `list_all`, `create`, `update`, `soft_delete`. Новые generic-методы добавлять в базу, а не копировать по файлам. `restore` в модели `Base` есть, в репозитории — нет; не описывать методы, которых нет в коде.

---

## DI

`app/api/deps.py` — только общее:

- `get_session` / `SessionDep` — `UnitOfWork` (commit / rollback на границе запроса);
- `get_current_user` / `CurrentUser`, `get_current_user_id` / `UserDep`;
- `require_permission(action, entity)`.

Фабрики сервисов — **рядом с роутами домена**, не в одном файле на всё приложение:

```
app/api/v1/parties/deps.py
app/api/v1/warehouse/deps.py
...
```

```python
def get_client_service(session: SessionDep) -> ClientService:
    return ClientService(ClientRepository(session))
```

Почему не `ServiceContainer`: FastAPI и так кэширует `Depends` на запрос. Контейнер на каждый запрос собирает все сервисы приложения и провоцирует `services.session` + ручную сборку репозиториев в хендлере.

Почему не один `dependencies.py` на 40 фабрик: тот же god-object, только функциями. Доменный `deps.py` импортирует только свой модуль.

Несколько сервисов в одном хендлере — два `Depends`, не контейнер.

---

## `core` и `infrastructure`

Держать **отдельно**. Разные потребители: `core` тянут роуты, middleware, скрипты; `infrastructure` — модели и репозитории.

| Пакет | Что сюда относится | Что не относится |
|---|---|---|
| `core` | config, security, context, exceptions, middleware (без записи в БД) | ORM, репозитории, HTTP-роуты |
| `infrastructure` | `orm_base`, `repo_base`, `uow`, engine/session factory, events, logging, внешние клиенты | JWT, RBAC, Pydantic-схемы API |

`core` не импортирует фичи (`accounts.models` и т.п.). `infrastructure` не импортирует FastAPI.

Сейчас граница дырявая (см. долг ниже). Цель — поправить размещение файлов, пакеты не сливать.

---

## Схемы (`app/api/v1/{feature}/schemas/`)

- `*Read` — вложенные объекты, `from_attributes=True` (через `BaseRead` или свой `ConfigDict`).
- `*Create` — FK как `id`, не вложенные read-модели.
- `*Update` — все поля optional.
- Не держать схемы в `routes.py`.

`app/files/schemas.py` — исключение раскладки, не образец.

---

## Транзакции, события, auth

- Одна сессия на HTTP-запрос: `get_session` → `UnitOfWork`. Commit при успехе, rollback при исключении.
- Фоновые задачи не ходят в `Depends`. Импорт: `ImportRunService` открывает `UnitOfWork` на файл (и на шаги журнала). Сервис заказов не коммитит.
- Обмен: `integration` — транспорт, адаптер, журнал, профиль (способ: FTP + пять папок). Принятие PORDER — `orders.InboundExchangeService`. Интеграция не делает `session.add` чужих сущностей.
- `event_bus` — in-process. Обработчик не должен рассчитывать на сессию запроса; если нужна БД — своя сессия. Не эмитить из репозитория.
- Auth: JWT в `core/security.py`. `CurrentUser` — когда нужен объект; `UserDep` — когда только id. Права — `require_permission`, не ручные `if user_id is None` в каждом хендлере.
- `set_current_user_id` в middleware заполняет ContextVar для `created_by_id` в ORM. Это не замена `require_permission`.

---

## Известные отклонения

Документ описывает **цель**. Сейчас код ей не равен:

1. `ServiceContainer` в `app/api/deps.py` собирает ~30 сервисов на запрос. Роуты часто его игнорируют.
2. Пять стилей инъекции: локальный `get_service` (parties), `services.xxx`, `Repository(services.session)`, ручной `Service(...)` в хендлере, голый `SessionDep`.
3. `BaseRepository` только у parties и warehouse; остальные репозитории копируют CRUD.
4. Сервисы бросают `ValueError`, роуты ловят выборочно.
5. `database.py` в `core`, UoW в `infrastructure`. Аудит пишется из `core/middleware.py` в `accounts.models.Audit`; `infrastructure/audit/` пустой.
6. `core/statuses.py` — доменные enum’ы, ими пользуются модели и схемы.

~~7. Topology / product groups ходят в репозиторий через `services.product._repo._s`.~~ Закрыто: `app/api/v1/warehouse/deps.py`.

По моделям (mixins вместо одного `Base`, partial unique, статусы в БД) — `docs/09_models_improvements.md`, это не этот документ.

Когда отклонение закрыто — вычеркнуть его здесь. Не заводить отдельный «шаг 1…5»: он гниёт быстрее кода.
