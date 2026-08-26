# integration — обмен с поклажедателем

Транспорт и перевод: откуда взять файл и как разобрать. **Не** создаёт заказы и документы — это `orders.InboundExchangeService.accept` / `OutboundExchangeService.accept`.

Почта, ЭДО, другая система — те же слоты позже (другой транспорт / адаптер). Сейчас живой канал: FTP + XML Зиландии (PORDER, ORDER).

Код: `app/integration/`. HTTP: `app/api/v1/integration/`. Фоновая задача: `app.tasks.run_import` → `ImportRunService` (Celery, очередь `imports`).

---

## Профиль = способ обмена

Один `IntegrationProfile` — один способ забрать документы у поклажедателя: транспорт + адаптер + реквизиты.

У поклажедателя способов может быть несколько (FTP основной и запасная папка). Один должен быть **по умолчанию**: обычный импорт и расписание идут только им. Запасной не пропадает — оператор один раз нажимает «Забрать сейчас» **на карточке этого способа**. Расписание запасной не трогает, иначе легко забрать одно и то же дважды.

Кнопка «Импорт» на списках заявок (`/orders/inbound`, `/orders/outbound`) — массовый прогон (тип документа `porder` / `order`), не выбор канала. Пошагово с исходящих: [flows/outbound-import.md](../flows/outbound-import.md).

**Сейчас в коде:** профилей у поклажедателя сколько угодно; флага «по умолчанию» нет; «Забрать сейчас» на карточке нет; прогон берёт все **активные** профили с FTP. Цель выше — ещё не реализована.

`source_type` на профиле — какой разбор (сейчас `zln` / `manual`). Транспорт и пути — в `config`. Адаптер в прогоне пока всегда `ZLNAdapter`, не из профиля.

---

## Модели

**IntegrationProfile**: `depositor_id`, `name`, `source_type`, `config` (JSONB).

В `config.ftp`:

| Ключ | Смысл |
|------|--------|
| `host`, `username`, `password` | доступ |
| `in_path` | входящие: откуда забираем заявки |
| `out_path` | исходящие: куда кладём подтверждения |
| `print_path` | печатные формы (PDF) |
| `archive_path` | архив успешно обработанных |
| `error_path` | файлы, которые не приняли |

Импорт **сейчас** ходит только во входящие (`in_path`). Без `in_path` профиль пропускается. Пустая папка — нормальный итог («файлов нет»), не ошибка. Подключение к FTP рвётся через 15 с, если хост не отвечает. **Исходящие ответы** кладутся в `out_path` (`ExportService` + `FTPService.upload`). PDF / архив / ошибки хранятся в конфиге, в прогоне не используются. Пароль FTP в карточке и в Read отдаётся как есть.

**IntegrationLog** / **IntegrationError**: прогресс прогона и ошибки строк.

---

## Поток импорта (PORDER)

1. HTTP создаёт лог, **сразу `commit`**, затем Celery (`POST /integrations/import`) — иначе ранний `GET /status` ловит 404 до commit UoW.
2. `ImportRunService`: активные профили, FTP, файлы из `in_path`.
3. `ZLNAdapter` → `InboundExchangeMessage` (контракт **orders**, без тегов XML). Нет `DOC_NO`, `LOC`, блока `VENDOR` / `VENDOR/ID` / `VENDOR/NAME`, `ITEMS` или `LN` — сообщение не собирается. Номера заказа в PORDER нет — `order_number` на заявке пустой.
4. `InboundExchangeService.accept(depositor_id=профиль)` — поставщик, заявка, всегда receipt (LOC обязателен).
5. Успех или пропуск дубликата: файл `porder_*` снимается с FTP. Ошибка — файл остаётся.
6. На файл — свой `UnitOfWork`. Сервис заказов не коммитит.
7. После успешного accept (не skip): событие `inbound_order.accepted_from_exchange` → `ExportService.export_pordrsp` → FTP `out_path`. Даты в XML — `order_date` заявки, TZ имени файла — Europe/Moscow. На дубликат ответа нет.

## Поток импорта (ORDER)

1–2. Как у PORDER; фильтр файлов `order_*`.
3. `ZLNAdapter` → `OutboundExchangeMessage`. Обязательны `DOC_NO`, `LOC`, `CUSTOMER` (ID+NAME), `DELIV_ADDR`, `LN`. `ITEMS` / `SUM` / `COLLECT` игнорируются. `DELIV=1` → доставка, иначе самовывоз. Без `DELIV_ADDR` сообщение не собирается.
4. `OutboundExchangeService.accept`: товары только из справочника (не создаём); адрес `get_or_create`; клиент `(code, delivery_address_id)`; без товара/адреса/клиента/LOC→VW — заказ не создаём, файл остаётся. Успех → событие `outbound_order.accepted_from_exchange` (deferred emit после commit) → подписчики delivery **и** `export_ordrsp`.
5. Успех или дубликат: `order_*` снимается с FTP. На дубликат ORDRSP не шлём.

## Ответный XML (выгрузка)

| Когда | Файл | Корневой тег | Строки LN |
|-------|------|--------------|-----------|
| После accept PORDER | `pordrsp_{номер}_{YYYYMMDD-HHMMSS}.xml` | `PORDRSP` | нет |
| После accept ORDER | `ordrsp_…` | `ORDRSP` | нет |
| После complete приёмки | `recadv_…` | `RECADV` | ITEM/LOT/DATE_EXP/UNIT/QNT из факта задания |
| После complete отбора | `desadv_…` | `DESADV` | то же; номер заказа — теги `ORDER_NO` / `ORDER_DATE` (не `ORD_*`) |

Профиль: первый активный с `config.ftp.out_path` у поклажедателя. `PARTNER` — `config.partner` / `ftp.partner` / `ZLN`. Флаги на заказе: `pordrsp_exported` / `recadv_exported` / `ordrsp_exported` / `desadv_exported`. События complete: `receiving_task.completed` / `picking_task.completed`. Подписчики регистрируются в `bootstrap_background_subscribers()` (main + Celery worker).

Код: `exporters/zln_xml.py`, `services/export_service.py`, `subscribers/export_handlers.py`.
---

## Экраны

Список: `/integrations/profiles`. Ссылка с строки — `/integrations/profiles/{id}` (не `/reference/...`: неизвестный путь уводит на главную).

Карточка: название, поклажедатель, тип источника, активность, FTP и пять папок. **Редактировать** — `/integrations/profiles/{id}/edit` (право `update` на `integrations`). После сохранения карточка берёт ответ PATCH, GET без кэша браузера.

Создание: `/integrations/profiles/new` — те же поля, включая пять папок.

Логи: `/integrations/logs` (`GET /api/v1/integrations/logs`), карточка `/integrations/logs/{id}` — статус, счётчики, сообщения и ошибки прогона.

---

## Файлы

| Файл | Роль |
|------|------|
| `services/ftp_service.py` | FTP (list/download/delete/upload) |
| `services/import_run_service.py` | Прогон: лог, FTP, адаптер, вызов `accept` |
| `services/export_service.py` | PORDRSP/ORDRSP/RECADV/DESADV → FTP `out_path` |
| `exporters/zln_xml.py` | Сборка XML |
| `subscribers/export_handlers.py` | Подписчики на accept/complete |
| `adapters/zln_adapter.py` | XML Зиландии → сообщение orders |
| `tasks.py` | Celery: свой Postgres-движок на задачу + `ImportRunService.run`. Воркер **не** перечитывает код сам — после правок `docker compose -f docker-compose.dev.yml restart celery_worker`. |

---

## API (`/api/v1/integrations`)

RBAC: `integrations`. Импорт: `app/api/v1/integration/routes_import.py`. Журнал: `routes/logs.py`.

| Метод | Путь |
|-------|------|
| CRUD | `/profiles`, `/profiles/{id}` |
| POST | `/import` — Celery, ответ `task_id` |
| GET | `/import/{task_id}/status` |
| GET | `/import/{task_id}/status/long` — ждёт до ~25 с смену лога, не отвечает сразу |
| GET | `/logs`, `/logs/{id}` — журнал импорта |
| GET | `/import/history` |
| GET | `/import/{task_id}/errors/excel` |

PATCH профиля после flush перечитывает строку (`updated_at` иначе не читается в async).

---

## Связи

Интеграция знает **orders** только как `InboundExchangeMessage` + `accept`. Не пишет таблицы склада, parties, documents.
