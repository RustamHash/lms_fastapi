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

`InboundOrderService`, `OutboundOrderService`, `ReturnOrderService` — CRUD с экрана. На create/update проверяют `DataScope`. Списки — `list_all(scope=...)`.

`InboundExchangeService.accept` — второй вход: заявка с обмена, без UI-скоупа (поклажедатель = профиль FTP). Дубликат номера — пропуск. Событие `inbound_order.accepted_from_exchange`.

Складской воркфлоу не в этом модуле: `ReceivingService.create_from_inbound` и `PickingService.create_from_outbound` (см. [warehouse.md](warehouse.md)). Заказ меняет статус (`task_created` → `in_progress` → `completed`); у inbound при недогрузе — `has_shortage`.

---

## API (`/api/v1`)

RBAC entity: `orders`.

Типично: список, создание, get/patch/delete по id, линии `/{id}/lines` и `PATCH/DELETE /lines/{line_id}`. Все три ресурса с `ScopeDep`.

Фильтр списков по скоупу уже есть. Пользователь поклажедателя не должен видеть чужие заказы.

---

## Связи

- **parties** — depositor, client/supplier, адрес.
- **warehouse** — `warehouse_id`, товар в строках.
- **documents** — `InboundExchangeService` создаёт receipt с `inbound_order_id`, если есть склад.
- **delivery** — `DeliveryOrder.outbound_order_id`.
- **integration** — только доставляет `InboundExchangeMessage`; не пишет таблицы заказов.

---

## Состояние

Скоуп поклажедатель+клиент на заказах уже в коде. Исполнение на складе — этап 3 (закрыт). XML-ответ партнёру и маппинг LOC склада — этап 4.
