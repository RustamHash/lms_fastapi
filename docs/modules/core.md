# core — сквозное приложение

Пакет без фичевых ORM. Его тянут роуты, middleware, скрипты. **Не** класть сюда репозитории и модели склада.

Код: `app/core/`.

---

## Файлы

| Файл | Назначение |
|------|------------|
| `config.py` | `Settings`: `DATABASE_URL`, JWT, DaData, CORS, логи. `.env` |
| `security.py` | хэш пароля, `create_access_token`, разбор JWT |
| `exceptions.py` | `BadRequestError` 400, `UnauthorizedError` 401, `ForbiddenError` 403, `NotFoundError` 404, `ConflictError` 409 |
| `database.py` | async engine / session factory (цель — перенести в infrastructure) |
| `middleware.py` | CORS, текущий user id в ContextVar, аудит |
| `context.py` | `get/set_current_user_id_context` для `created_by_id` |
| `statuses.py` | `OrderStatus`, `DocumentStatus`, `TaskStatus`, `DeliveryStatus` + русские label |
| `list_defaults.py` | дефолты колонок списков |
| `model_rebuilder.py` | `rebuild_all_models()` из-за циклов Pydantic |

`core` не импортирует `app.accounts.models` и прочие фичи. Сейчас граница дырявая: middleware пишет в `Audit`. Цель — поправить размещение, пакеты не сливать. См. [ARCHITECTURE.md](../../ARCHITECTURE.md).

---

## Статусы

Enum в Python, в БД колонки пока `String`. Невалидное значение не режется CHECK’ом (долг моделей). Фронт берёт label отсюда / `statusLabels.ts`.
