# warehouse — склад

Топология (склад → зона → ряд → ячейка), товары поклажедателя, партии, LPN, снимок остатка, журнал движений, складские задания.

Код: `app/warehouse/`. HTTP: `app/api/v1/warehouse/`. Фабрики: `app/api/v1/warehouse/deps.py`.

---

## Зачем модуль

Исполнение заказа на полу: куда лежит товар, сколько доступно, какое задание у оператора. Писать остаток должен только `StockService` (движение + баланс в одной транзакции). Роуты не делают `session.add(StockBalance)`.

---

## Топология

```
Warehouse (физический)
  ├── VirtualWarehouse  (нарезка по поклажедателю)
  └── Zone
        └── Row
              └── Location  (ячейка)
```

`Warehouse.address_id` → parties. `VirtualWarehouse` — `(depositor_id, warehouse_id, code)`.

API: `/api/v1/warehouse/topology/{warehouses,virtual-warehouses,zones,rows,locations}`  
RBAC entity: `warehouse`.

Сервисы: `WarehouseService`, `VirtualWarehouseService`, `ZoneService`, `RowService`, `LocationService`.

---

## Номенклатура

| Модель | Смысл |
|--------|--------|
| `ProductGroup` | группа |
| `Product` | товар поклажедателя, `external_id` + `sku`, вес/объём |
| `Package` | упаковка / вложенность |
| `ProductLocation` | допустимые/предпочтительные ячейки |
| `Batch` | партия (срок годности — для FEFO) |
| `LPN` | паллета / грузоместо, уникальный `number` |

API под `/api/v1/warehouse/`: `products`, `product-groups`, `packages`, `product-locations`, `batches`, `lpns`.  
RBAC: `products`, `batches`, `lpns`.

`ProductService.create` отвергает дубль `(depositor_id, external_id)`.

---

## Остаток

`StockBalance` — снимок: `(product_id, location_id, batch_id, lpn_id)` + `quantity`, `reserved_quantity`. LPN обязателен: сначала грузоместо, потом товар. Unique `(product_id, location_id, batch_id, lpn_id)`. CHECK: количество ≥ 0, резерв ≥ 0 и не больше количества.

`StockMovement` — журнал: `direction` in/out, `quantity`, `moved_at` (момент движения, не `created_at`), `moved_by_id`, опционально `document_id` и `task_line_id`.

`StockService` — единственный writer остатка и движения в одной транзакции: `add_stock`, `remove_stock`, `move_stock`, `get_balance` (`FOR UPDATE`), `get_available_quantity` (SQL `SUM`). Гонка двух insert ловится unique: повторный `get_balance` и плюс количество. Без LPN или партии — `BadRequestError`.

API: `GET /warehouse/stock`, `POST /warehouse/stock/{add,remove,move}`.  
RBAC: `stock`.

---

## Задания

`Task` + `TaskLine`: `task_type`, связь с `documents_document`, исполнитель, план/факт qty, from/to location, LPN, batch.

API: `/warehouse/tasks`, `/tasks/list`, `POST /tasks/from-document`, `start`, `complete`.  
RBAC: `tasks` (`execute` / `complete` на переходы).

Сейчас задания ещё близки к generic CRUD. Цель этапа 3: приёмка и FEFO-отбор как воркфлоу из inbound/outbound, не ручное создание Task с UI как основной путь. `plan_qty`/`fact_qty` сейчас `Integer`, остаток — `Numeric`.

`PlacementService` — размещение; либо встроить в приёмку, либо убрать, если мёртвый.

---

## Связи

- **parties** — depositor на товаре и виртуальном складе.
- **documents** — задание и движение могут ссылаться на документ.
- **orders** — в целевом потоке заказ порождает задание; сейчас связь ещё слабая.
- **accounts** — `assignee_id` на задании.

Фича не импортирует чужой `repository`. Остаток менять только через `StockService`.

---

## Состояние

Этап 1 (DI склада) закрыт: роуты без `*Repository` и без `Services`.  
Этап 2 закрыт: unique остатка, LPN обязателен, `moved_at` на движении, pytest гонки.  
Этап 3 (приёмка, FEFO) — в очереди `plans/STATUS.md`.

Журнал `StockMovement` без отдельного REST. `PlacementService` (FEFO-размещение) в коде есть, к роутам не подключён. Список товаров фильтруется query `depositor_id`, не `DataScope`.
