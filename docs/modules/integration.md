# integration — обмен с поклажедателем

Транспорт и перевод: FTP, профили, журнал, адаптер XML. **Не** создаёт заказы и документы.

Код: `app/integration/`. HTTP: `app/api/v1/integration/`. Фоновая задача: `app.tasks.run_import` → `ImportRunService` (Celery, очередь `imports`).

---

## Модели

**IntegrationProfile**: `depositor_id`, `name`, `source_type`, `config` (JSONB: хост FTP, пути, формат).

**IntegrationLog** / **IntegrationError**: прогресс прогона и ошибки строк.

---

## Поток импорта (PORDER)

1. HTTP создаёт лог и ставит Celery.
2. `ImportRunService`: активные профили, FTP, скачать файл.
3. `ZLNAdapter` → `InboundExchangeMessage` (контракт модуля **orders**, без тегов XML).
4. `InboundExchangeService.accept(depositor_id=профиль, message)` — создание заявки в orders.
5. Успех или пропуск дубликата: файл `porder_*` снимается с FTP. Ошибка — файл остаётся.
6. На файл — свой `UnitOfWork` (commit/rollback). Сервис заказов не коммитит.

ORDER с обмена пока отклоняется адаптером («не принимается»). Ответный XML — подписка на событие заказа, этап 4 (`ExportService` ещё нет).

---

## Файлы

| Файл | Роль |
|------|------|
| `services/ftp_service.py` | FTP |
| `services/import_run_service.py` | Прогон: лог, FTP, адаптер, вызов `accept` |
| `adapters/zln_adapter.py` | XML Зиландии → сообщение orders |
| `tasks.py` | Celery: модели + `ImportRunService.run` |

---

## API (`/api/v1/integrations`)

RBAC: `integrations`. Профили: `/profiles`. Импорт — `app/api/v1/integration/routes_import.py`.

| Метод | Путь |
|-------|------|
| CRUD | `/profiles`, `/profiles/{id}` |
| POST | `/import` — Celery, ответ `task_id` |
| GET | `/import/{task_id}/status` |
| GET | `/import/{task_id}/status/long` — long-poll ~25 с |
| GET | `/import/history` |
| GET | `/import/{task_id}/errors/excel` |

---

## Связи

Интеграция знает **orders** только как `InboundExchangeMessage` + `accept`. Не импортирует репозитории склада, parties, documents.
