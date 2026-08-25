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

`uow.py` — `UnitOfWork`: commit при успехе, затем `flush_pending_events(session)`; при исключении — `discard_pending_events` и rollback. HTTP: `get_session` в `app/api/deps.py`. Celery (`app/tasks.py`) не берёт общий пул FastAPI: на задачу свой движок `create_worker_engine()` (`NullPool`) внутри `asyncio.run`.

---

## События

`events/events.py` — in-process `EventBus` (`subscribe` / `emit`). Сервисы вызывают `schedule_event(session, …)` — emit после `commit` в [`uow.py`](../infrastructure/uow.py). При rollback очередь событий сбрасывается. Ошибка хендлера логируется, остальные продолжают.

`event_types.py`:

- `import.completed` / `import.failed`
- `inbound_order.accepted_from_exchange` / `outbound_order.accepted_from_exchange` / `outbound_order.created`
- `document.created` / `document.status_changed`
- `delivery_order.*`, `route.assigned`
- `task.created` / `task.completed`

Эмитить через **`schedule_event(session, …)`** из сервиса, не `emit` напрямую и не из репозитория. Подписчику нужна БД — своя сессия + UoW (пример: `app/delivery/subscribers/outbound_handlers.py`, `app/notifications/services/dispatcher.py`).

---

## Прочее

- `external/dadata.py` — подсказки адресов. Единственный геокодер.
- `logging/` — файлы `logs/app.log`, `error.log`, `sql.log`.
- `infrastructure/audit/` — пустой; запись аудита пока из `core/middleware`.
