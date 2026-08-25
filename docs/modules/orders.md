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

Статусы: `OrderStatus` в `app/core/statuses.py` — `new` → `document_created` → `task_created` → `in_progress` → `completed` / `cancelled`. В колонке пока свободная строка.

---

## Поля (важное)

**Inbound:** `depositor_id`, `warehouse_id`, `supplier_id` (клиент-поставщик), даты, `pordrsp_exported` / `recadv_exported` (ответный XML — генерация ещё в этапе 4), `has_shortage`. Складской документ прихода ссылается на заказ через `documents_document.inbound_order_id`.

**Outbound:** `depositor_id`, `client_id` (обязателен), адрес/контакт доставки, `needs_delivery`, `delivery_only` (без склада), вес/места, флаги экспорта `ordrsp` / `desadv`, статус доставки отдельно от статуса заказа.

Строки: товар, количество, партия по необходимости.

---

## Сервисы

`InboundOrderService`, `OutboundOrderService`, `ReturnOrderService`.

CRUD заказа и строк. На create/update проверяют `DataScope` (`ForbiddenError`, если чужой depositor/client). Списки — `list_all(scope=...)`.

Ещё нет: «создать задание приёмки из inbound» и FEFO-план отбора из outbound как основной сценарий (этап 3).

---

## API (`/api/v1`)

RBAC entity: `orders`.

Типично: список, создание, get/patch/delete по id, линии `/{id}/lines` и `PATCH/DELETE /lines/{line_id}`. Все три ресурса с `ScopeDep`.

Фильтр списков по скоупу уже есть. Пользователь поклажедателя не должен видеть чужие заказы.

---

## Связи

- **parties** — depositor, client/supplier, адрес.
- **warehouse** — `warehouse_id`, товар в строках.
- **documents** — целевой шаг после заявки (ещё не жёстко связан в сервисе заказа).
- **delivery** — `DeliveryOrder.outbound_order_id`.
- **integration** — создаёт inbound/outbound из XML; дубликат номера пропускает.

---

## Состояние

Скоуп поклажедатель+клиент на заказах уже в коде. XML-ответ партнёру и маппинг LOC склада — этап 4. Не наращивать новые типы заказов до конца этапа 3.
