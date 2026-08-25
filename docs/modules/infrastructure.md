# infrastructure — персистентность и I/O

Технический слой: ORM-база, generic-репозиторий, единица работы, события, логи, внешние HTTP-клиенты. **Не** JWT, не RBAC, не FastAPI-роуты.

Код: `app/infrastructure/`.

---

## ORM и репозиторий

`orm_base.py` — `Base`: `id`, `is_active`, timestamps, `created_by_id` / `updated_by_id` (из ContextVar), soft delete (`is_deleted`, `deleted_at`, `deleted_by_id`). Методы `soft_delete` / `restore` / `activate`.

Разнести на миксины (логи без soft delete и т.д.) — [09_models_improvements.md](../09_models_improvements.md), не отдельный «рефакторинг всего Base» вне этапов 2–3.

`repo_base.py` — `BaseRepository`: `get_by_id`, `list_all`, `create`, `update`, `soft_delete`. Новые generic-методы — сюда, не копипаста по файлам. `restore` в модели есть, в репозитории нет.

Сейчас на `BaseRepository` в основном parties и warehouse; остальные репозитории часто дублируют CRUD (этап 7).

---

## Транзакции

`uow.py` — `UnitOfWork`: commit при успехе, rollback при исключении. HTTP: `get_session` в `app/api/deps.py`. Celery (`app/tasks.py`) не берёт общий пул FastAPI: на задачу свой движок `create_worker_engine()` (`NullPool`) внутри `asyncio.run`.

---

## События

`events/events.py` — in-process `EventBus` (`subscribe` / `emit`). Ошибка хендлера логируется, остальные продолжают.

`event_types.py`:

- `import.completed` / `import.failed`
- `inbound_order.accepted_from_exchange` / `outbound_order.accepted_from_exchange`
- `document.created` / `document.status_changed`
- `delivery_order.*`, `route.assigned`
- `task.created` / `task.completed`

Эмитить из **сервиса**, не из репозитория. Подписчику нужна БД — своя сессия.

---

## Прочее

- `external/dadata.py` — подсказки адресов. Единственный геокодер.
- `logging/` — файлы `logs/app.log`, `error.log`, `sql.log`.
- `infrastructure/audit/` — пустой; запись аудита пока из `core/middleware`.
