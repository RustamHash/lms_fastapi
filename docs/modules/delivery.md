# delivery — доставка

Заявки на доставку, водители, транспорт, маршруты и отклонения. Складской отгрузке не обязан: есть `delivery_only` на исходящем заказе.

Код: `app/delivery/`. HTTP: `app/api/v1/delivery/`.

---

## Модели

| Класс | Таблица | Смысл |
|-------|---------|--------|
| `DeliveryOrder` | `delivery_order` | заявка: номер, даты/окно, контакт, статус, связи |
| `DeliveryDeviation` | `delivery_deviation` | отклонение по заявке |
| `Driver` | | водитель |
| `Vehicle` | | ТС |
| `Route` + `RouteLine` | | маршрут и точки |

`DeliveryOrder` может ссылаться на `contract_id`, `document_id`, `outbound_order_id`, `parent_id` (дробление).

Статусы: `DeliveryStatus` — `created`, `assigned`, `in_transit`, `delivered`, `failed`, …

Сервисы: `DeliveryOrderService`, `DeliveryFromOutboundService`, `DriverService`, `VehicleService`, `RouteService`, `RouteLineService`, `DeviationService`. List/get/patch/delete заявок — со `DataScope`. POST создания скоуп не проверяет.

События: `delivery_order.*`, `route.assigned`.

---

## Автосоздание из исходящего заказа

`DeliveryFromOutboundService` (`services/from_outbound_service.py`) — идемпотентный `ensure_for_outbound(order_id)`:

- Условие: `OutboundOrder.needs_delivery == True`.
- Если `DeliveryOrder` с этим `outbound_order_id` уже есть — возвращает существующую.
- Иначе создаёт заявку: `number` = номер outbound, `delivery_date` = `shipping_date` или `order_date`, контакт и комментарий из outbound, `status` = `created`; на outbound ставит `delivery_status` = `created`.
- Эмитит `delivery_order.created` через `DeliveryOrderService` (`schedule_event` после commit).

Подписчики (`subscribers/outbound_handlers.py`), регистрация через `bootstrap_background_subscribers()` (FastAPI `main` и Celery worker):

| Событие | Когда |
|---------|--------|
| `outbound_order.accepted_from_exchange` | импорт ORDER (`OutboundExchangeService.accept`) |
| `outbound_order.created` | ручной POST/PATCH outbound с `needs_delivery` |

Обработчик открывает свой `UnitOfWork` (данные outbound уже закоммичены). Пошагово импорт: [outbound-import.md](../flows/outbound-import.md).

---

## API (`/api/v1`)

| Префикс | RBAC |
|---------|------|
| `/delivery/orders` | `delivery` |
| `/delivery/drivers` | `drivers` |
| `/delivery/vehicles` | `vehicles` |
| `/delivery/routes` | `routes` |
| `/deviations` | `delivery` (ответ `dict`, не схема); есть GET `/{id}` |
| `/route-lines` | `routes` (тоже `dict`); есть GET `/{id}` |

Роуты list/get/patch/delete заявок ещё ходят в `DeliveryOrderRepository` через `Services` (этап 7). POST `/delivery/orders` — через `DeliveryOrderService.create`.

---

## Связи

- **orders** — исходящий заказ с `needs_delivery`; автосоздание delivery — см. выше.
- **documents** — складской документ отгрузки.
- **parties** — договор перевозки, адрес клиента.
- **accounts** — скоуп поклажедателя/клиента на заявках (через join на `outbound_order_id`).

---
