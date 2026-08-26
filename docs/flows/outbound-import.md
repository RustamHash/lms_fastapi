# Импорт с `/orders/outbound`

Пошаговый путь: иконка «Импорт» на списке исходящих → диалог → `POST /import` → Celery → FTP → ORDER → исходящая заявка.

Экран: FastAPI `:8080` отдаёт SPA; запросы идут на `/api/v1/...`.

Код: `frontend/src/pages/OutboundOrdersPage.tsx`, `ImportDialog`, `app/api/v1/integration/routes_import.py`, `ImportRunService`, `ZLNAdapter`, `OutboundExchangeService`.

---

## 1. Страница и диалог

1. `/orders/outbound` → кнопка «Импорт» → `ImportDialog` с `documentType="order"`.
2. Сразу `POST /api/v1/integrations/import` с `{ "document_type": "order" }`.
3. Лог в БД + `commit` до Celery; фронт поллит `/status` и `/status/long`.

## 2. Воркер

4. Активные профили, FTP `in_path`, файлы `order_*`.
5. `ZLNAdapter.parse` → `OutboundExchangeMessage` или ошибки.
6. `OutboundExchangeService.accept(depositor_id=профиль)`.

### Контракт ORDER (обязательное)

| Тег | Назначение |
|-----|------------|
| `DOC_NO` | номер заявки |
| `LOC` | виртуальный склад поклажедателя |
| `CUSTOMER/ID`, `CUSTOMER/NAME` | клиент (+ опционально LEGAL_NAME, INN, KPP, USE_EDO) |
| `DELIV_ADDR` | адрес доставки (без fallback на CONSIG_ADDR) |
| `LN` | строки: ITEM = external_id товара, QNT |

Игнорируются: `ITEMS`, `SUM`, `COLLECT`. `DELIV=1` → `needs_delivery`, иначе самовывоз. Снимки: `CONSIG`, `CONSIG_CONT`, `ADDR_COM`.

### Правила accept

- Товар **не** создаём; нет SKU в справочнике → ошибка, заказ нет, файл остаётся.
- Адрес через DaData `get_or_create`; клиент `get_or_create(code, delivery_address_id)`. Сбой → заказ нет.
- Нет VW по LOC → заказ нет.
- Дубликат `(depositor_id, number)` → skip, файл снимаем.
- Успех → `OutboundOrder` + lines + событие `outbound_order.accepted_from_exchange` (`needs_delivery`, `client_id`, …). Подписчик delivery создаёт `DeliveryOrder` **после commit** (deferred emit в UoW).

## 3. Итог

С исходящих массовый прогон создаёт расходные заявки из XML ORDER. При `needs_delivery` подписчик создаёт `DeliveryOrder` после commit. После успешного accept (не skip) выгружается ORDRSP в `out_path`; после complete отбора — DESADV.

Входящие (`porder`) — зеркальный контур с созданием номенклатуры и receipt.
