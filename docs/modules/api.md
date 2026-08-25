# api — HTTP-слой `/api/v1`

Сборка роутеров, общие зависимости, метаданные полей для динамических списков. Не домен: бизнес-правила живут в фичах.

Код: `app/api/` + исключение `app/files/routes.py`.

---

## Сборка

`app/main.py` поднимает FastAPI, middleware, exception handlers, `api_router`.

`app/api/v1/router.py` — префикс `/api/v1`, подключает parties, accounts, warehouse, orders, delivery, documents, notifications, integration, files, meta.

Фабрики сервисов склада — `app/api/v1/warehouse/deps.py`. Parties — `app/api/v1/parties/deps.py`. Остальные фичи ещё часто берут `Services` из `ServiceContainer` в `app/api/deps.py` (этап 7).

---

## Общие Depends (`app/api/deps.py`)

| Зависимость | Смысл |
|-------------|--------|
| `get_session` / `SessionDep` | `UnitOfWork`: commit / rollback на запрос |
| `CurrentUser` | объект `User`, обязательный JWT |
| `UserDep` | только id (может быть `None`) |
| `ScopeDep` | `DataScope` из привязок пользователя |
| `require_permission(action, entity)` | RBAC → `ForbiddenError` |
| `Services` | контейнер сервисов (не использовать на новых роутах склада) |

JWT: `OAuth2PasswordBearer`, `tokenUrl=/api/v1/auth/token`.

---

## Meta

`app/api/v1/meta.py`, префикс `/api/v1/entities`.

| Метод | Путь |
|-------|------|
| GET | `/` — ключи сущностей |
| GET | `/{entity}/fields` — поля Pydantic-схемы для колонок UI |

Ключ должен совпадать с `entityKey` в `features/*/config.ts` и записью в `MODEL_MAP`. Новый список на фронте без записи здесь — колонки не подтянутся автоматически.

---

## Схемы

`app/api/v1/{feature}/schemas/`: `*Read` с `from_attributes`, `*Create` с FK-id, `*Update` все optional. Не класть схемы в `routes.py` (исключение — `files`).
