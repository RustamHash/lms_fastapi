# integration — обмен с поклажедателем

Профили подключения (FTP и др.), журнал прогонов, разбор входящих XML и создание заказов/документов/клиентов.

Код: `app/integration/`. HTTP: `app/api/v1/integration/`. Фоновая задача: `app.tasks.run_import` (Celery, очередь `imports`).

---

## Модели

**IntegrationProfile**: `depositor_id`, `name`, `source_type`, `config` (JSONB: хост FTP, пути, формат).

**IntegrationLog** / **IntegrationError**: прогресс прогона и ошибки строк.

---

## Поток импорта

1. API или Celery берёт профиль, качает файлы (`FTPService`).
2. Адаптер (`ZLNAdapter`) → универсальный dict (`document_type`, номер, строки).
3. `IntegrationService.process_document` возвращает `(заказ, ошибки, skipped)`:
   - дубликат inbound/outbound по `(depositor_id, number)` — `skipped=True`, не ошибка;
   - товары — `ProductService.get_or_create`;
   - PORDER: поставщик `ClientService.get_or_create` (без адреса), lookup `VirtualWarehouse` по LOC, заказ + строки, при найденном складе — документ `receipt` с `inbound_order_id`.

**PORDER (сделано).** Дата заказа: `DOC_DATE` / `DELIV_DATE` / сегодня. Пустой LOC — заказ без склада и без документа (`warehouse_id` документа обязателен). Неизвестный LOC — ошибка, виртуальный склад не создаётся. Успех или дубликат: файл `porder_*` снимается с FTP. Ответный XML нет.

**ORDER (отгрузка).** Парсер есть; адрес/DaData и автосоздание VW ещё ломают живой прогон — не этот фикс.

Генерация `pordrsp` / `ordrsp` / `desadv` / `recadv` и таблица маппинга LOC — этап 4.

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

Задача `app.tasks.run_import` (очередь `imports`, Redis). Своя сессия, не `Depends`. Адаптер пока один: ZLN.

---

## Связи

Тянет сервисы **parties**, **orders**, **documents**, **delivery**, **warehouse** (товары). Это оркестратор обмена, не место для SQL чужих таблиц на постоянку (сейчас часть запросов ещё прямо в сессии сервиса — техдолг этапа 7).
