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

Сервисы: `DeliveryOrderService`, `DriverService`, `VehicleService`, `RouteService`, `RouteLineService`, `DeviationService`. List/get/patch/delete заявок — со `DataScope`. POST создания скоуп не проверяет.

События: `delivery_order.*`, `route.assigned`.

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

Роуты заявок ещё ходят в `DeliveryOrderRepository` через `Services`, не через сервис (этап 7).

---

## Связи

- **orders** — исходящий заказ с `needs_delivery`.
- **documents** — складской документ отгрузки.
- **parties** — договор перевозки, адрес клиента.
- **accounts** — скоуп поклажедателя/клиента на заявках.

Интеграция может создать `DeliveryOrder` вместе с outbound.
