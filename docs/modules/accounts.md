# accounts — пользователи, RBAC, скоуп

Пользователи системы, роли с JSON-правами, привязка к поклажедателям и клиентам, журнал аудита, персональные настройки таблиц.

Код: `app/accounts/`. HTTP: `app/api/v1/accounts/`.

---

## Зачем модуль

3PL-склад обслуживает несколько поклажедателей. Сотрудник склада видит всё; менеджер поклажедателя — только своих; торговый агент — своих клиентов. Права на экраны и действия задаются ролями, не хардкодом в каждом роуте.

---

## Состав

| Путь | Роль |
|------|------|
| `models/` | `User`, `Role`, `user_roles`, `UserDepositor`, `UserClient`, `Audit`, `UserSettings`, `UserTableSettings`, `UserListPreset` |
| `permissions.py` | `has_permission`, `get_all_permissions`, `has_group_access` |
| `permissions_catalog.py` | белый список entity/action |
| `scope.py` | `DataScope`, `build_scope` |
| `repository.py` | репозитории пользователей, ролей, аудита, настроек |
| `services/` | `UserService`, `RoleService`, `AuditService`, `ListSettingsService`, `TableSettingsService` |
| `app/api/v1/accounts/` | роуты и схемы |

---

## Модели

**User** (`accounts_user`): `username`, `password_hash`, `email`, `phone`, `is_superuser`, `extra_permissions` (JSONB поверх ролей). Partial unique на живой `username` / `email`.

**Role** (`accounts_role`): `code`, `name`, `permissions` — `{entity: [action, ...]}`. M2M через `accounts_user_roles`.

**UserDepositor** / **UserClient**: привязки скоупа. Пустой список поклажедателей = unrestricted.

**Audit** (`accounts_audit`): журнал действий (пишут middleware и сервисы).

Настройки списков: колонки, пресеты фильтров на пользователя.

Проверка прав живёт в `permissions.py`, не в методах ORM. `User.has_permission` делегирует туда.

---

## RBAC

Каталог: `MODULES` + `ACTIONS` в `permissions_catalog.py`. Неизвестный entity/action при сохранении роли — `ValueError`.

Действия: `view`, `create`, `update`, `delete`, `execute`, `complete`, `approve`, `cancel`.

На эндпоинте:

```python
dependencies=[Depends(require_permission("view", "clients"))]
```

`is_superuser` проходит всё. Иначе объединяются права ролей и `extra_permissions`.

Новый экран/API: добавить код в `MODULES` / `MODULE_LABELS`, повесить `require_permission`, обновить эту страницу и UI ролей.

---

## Скоуп данных

`build_scope(user)` → `DataScope`:

| Привязки | Режим |
|----------|--------|
| нет `depositor_ids` | `unrestricted=True` — видит все данные |
| есть поклажедатели, нет клиентов | фильтр по `depositor_id` |
| есть и клиенты | фильтр по depositor **и** `client_id` |

Хелперы: `allows_depositor`, `allows_client`, `filter_depositor`, `filter_client`.

Скоуп применяют клиенты, три типа заказов и заявки на доставку (кроме POST). Товары и поклажедатели пока не фильтруются. Не подменять скоуп ручными `if user_id` в роуте.

Зависимость: `get_data_scope` в `app/api/deps.py`.

---

## API

База: `/api/v1`.

| Метод | Путь | Право |
|-------|------|--------|
| POST | `/auth/token` | публичный (OAuth2 password) |
| GET | `/auth/me` | текущий пользователь + permissions + scope ids |
| POST | `/auth/register` | закрыт (404) |
| CRUD | `/users` | `users` |
| GET/PUT | `/users/{id}/roles`, `/depositors`, `/clients`, `/permissions` | `users` |
| CRUD | `/roles` | `roles` |
| GET | `/permissions/available` | каталог (`view` / `roles`) |
| GET/POST | `/audit` | `audit` |
| GET | `/audit/{id}` | `audit` |
| CRUD | `/user-settings`, `/user-depositors` | `users` |
| GET/PUT/DELETE | `/table-settings/{entity_key}` | авторизован, без `require_permission` |
| CRUD | `/list-presets/{entity_key}` | то же |

JWT: `app/core/security.py`. `tokenUrl` = `/api/v1/auth/token`.

Настройки таблиц — свои пресеты текущего пользователя; отдельного RBAC нет.

---

## Связи

- **parties** — FK на `Depositor` / `Client` в привязках пользователя.
- **все фичи** — `require_permission` и часто `DataScope`.
- **core/middleware** — `set_current_user_id` для `created_by_id` в ORM; аудит пишется из middleware в модель `Audit` (долг: должно уйти в `infrastructure/audit`).

---

## Состояние

- Роуты accounts ещё на `ServiceContainer` (`Services`), не на доменном `deps.py` (этап 7).
- `Role.permissions` — свободный JSONB, схема только через `validate_permissions_map`.
- Регистрация закрыта; пользователей создаёт админ или `scripts/create_superuser.py`.
