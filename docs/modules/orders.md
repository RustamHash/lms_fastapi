# orders — заявки на приёмку, отгрузку, возврат

Три типа заказов поклажедателя. Это заявки, не складские документы: документ и задание живут в `documents` / `warehouse`.

Код: `app/orders/`. HTTP: `app/api/v1/orders/`.

---

## Типы

| Модель | Таблица | API | Смысл |
|--------|---------|-----|--------|
| `InboundOrder` + `InboundOrderLine` | `orders_inbound` | `/inbound-orders` | заявка на приёмку (часто из XML `porder`) |
| `OutboundOrder` + `OutboundOrderLine` | `orders_outbound` | `/outbound-orders` | заявка на отгрузку (`order`) |
| `ReturnOrder` + `ReturnOrderLine` | `orders_return` | `/return-orders` | возврат |

Unique: `(depositor_id, number)` на inbound и outbound.

Статусы: `OrderStatus` в `app/core/statuses.py` — `new` → `document_created` → `task_created` → `in_progress` → `completed` / `cancelled`. На карточке и в списке входящих — русские подписи (`Документ создан` и т.д.).

---

## Поля (важное)

**Inbound:** `depositor_id`, `number` (номер заявки, `DOC_NO`), `order_number` (номер заказа, пока необязателен — в PORDER нет), `loc_code` (код склада = `LOC`, обязателен), `warehouse_id` (физический склад по маппингу виртуального), `supplier_id` (обязателен; `supplier_code` — снимок кода), даты, `pordrsp_exported` / `recadv_exported` (ответный XML после accept / complete приёмки), `has_shortage`. Складской документ прихода ссылается на заказ через `documents_document.inbound_order_id`.

**Outbound:** `depositor_id`, `client_id` (обязателен), адрес/контакт доставки, `needs_delivery`, `delivery_only` (без склада), вес/места, флаги экспорта `ordrsp_exported` / `desadv_exported`, статус доставки отдельно от статуса заказа.

Строки: товар, количество, партия по необходимости.

---

## Сервисы

`InboundOrderService`, `OutboundOrderService`, `ReturnOrderService` — CRUD с экрана. На create/update проверяют `DataScope`. Списки — `list_all(scope=...)`.

`InboundExchangeService.accept` — второй вход: заявка с обмена, без UI-скоупа (поклажедатель = профиль интеграции). Обязательны поставщик (`VENDOR` с `ID` и `NAME`) и код склада (`LOC` → `loc_code`, lookup виртуального склада). Без LOC сообщение не собирается; без VW — ошибка, заказ не создаётся. `order_number` с обмена пока пустой. Дубликат номера заявки — пропуск. Событие `inbound_order.accepted_from_exchange` → PORDRSP. Всегда создаётся складской документ прихода (receipt).

`OutboundExchangeService.accept` — ORDER с обмена: клиент+`DELIV_ADDR`, товары только существующие, `needs_delivery` из `DELIV`. Событие `outbound_order.accepted_from_exchange` (deferred emit) → delivery + ORDRSP. Складской shipment-документ пока не создаётся (FK `outbound_order_id` на Document ещё нет).

Кнопка импорта на списках заявок запускает обмен (см. [integration.md](integration.md)), не CRUD этого модуля. Пошагово ORDER: [outbound-import.md](../flows/outbound-import.md).

Складской воркфлоу не в этом модуле: `ReceivingService.create_from_inbound` и `PickingService.create_from_outbound` (см. [warehouse.md](warehouse.md)). Заказ меняет статус (`task_created` → `in_progress` → `completed`); у inbound при недогрузе — `has_shortage`. Complete приёмки/отбора → RECADV/DESADV (см. integration).

---

## API (`/api/v1`)

RBAC entity: `orders`.

Типично: список, создание, get/patch/delete по id, линии `/{id}/lines` и `PATCH/DELETE /lines/{line_id}`. Все три ресурса с `ScopeDep`.

Карточка входящего `/orders/inbound/:id`: шапка (в т.ч. физический склад `warehouse_name` по `warehouse_id`, LOC отдельно) и вкладки **План** / **Факт** / **Расхождения**. Данные: `GET /inbound-orders/{id}` + `GET /warehouse/receiving/inbound/{id}`.

Карточка исходящего `/orders/outbound/:id`: та же шапка+вкладки. Данные: `GET /outbound-orders/{id}` + `GET /warehouse/picking/outbound/{id}`. Сверка по `product_id` (строки FEFO-задания не 1:1 со строкой заявки).

Фильтр списков по скоупу уже есть. Пользователь поклажедателя не должен видеть чужие заказы.

---

## Связи

- **parties** — depositor, client/supplier, адрес.
- **warehouse** — `loc_code` (LOC) и `warehouse_id`, товар в строках.
- **documents** — `InboundExchangeService` при accept всегда создаёт receipt с `inbound_order_id` (LOC обязателен).
- **delivery** — `DeliveryOrder.outbound_order_id`.
- **integration** — доставляет `InboundExchangeMessage` / `OutboundExchangeMessage`; не пишет таблицы заказов.

---

## Состояние

Скоуп поклажедатель+клиент на заказах уже в коде. Исполнение на складе — этап 3. XML-ответ партнёру (PORDRSP/ORDRSP/RECADV/DESADV) и LOC→VW — в коде (этап 4).
