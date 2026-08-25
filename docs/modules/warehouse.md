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

## Задания и воркфлоу

`Task` + `TaskLine`: `task_type` (`receiving` / `picking`; movement и inventory — этап 6), связь с документом и/или заказом (`inbound_order_id` / `outbound_order_id`), исполнитель, `plan_qty`/`fact_qty` (`Numeric(20,3)`), from/to location, LPN, batch, флаг `reserved` на строке отбора.

Основной путь — не generic CRUD:

| Сервис | Откуда | Что делает |
|--------|--------|------------|
| `ReceivingService` | inbound | задание приёмки, факт (партия обязательна, LPN создаётся если не передан), расхождение план/факт (`ReceivingDiscrepancy`), закрытие (недогруз — с `confirm_shortage`), сторно движения через `remove_stock` |
| `PickingService` | outbound | задание отбора, FEFO-план (`Batch.expiration_date`, nulls last, по складу ячейки), резерв, отбор = `unreserve` + `remove_stock`, закрытие |

`PlacementService` — запасной поиск ячейки в `receive_line`, если у строки ещё нет `to_location_id`. Создание из inbound **требует** `receiving_location_id`.

API воркфлоу (RBAC entity `tasks`):

- `POST /warehouse/receiving/from-inbound` `{inbound_order_id, receiving_location_id}`
- `POST /warehouse/receiving/lines/{id}/receive`
- `POST /warehouse/receiving/{task_id}/complete` `{confirm_shortage}`
- `POST /warehouse/receiving/movements/{id}/cancel`
- `POST /warehouse/picking/from-outbound` `{outbound_order_id}`
- `POST /warehouse/picking/{task_id}/plan`
- `POST /warehouse/picking/lines/{id}/pick`
- `POST /warehouse/picking/{task_id}/complete`

Generic `/warehouse/tasks` (CRUD, `from-document`, `complete_line`) ещё есть; для приёмки и отбора это не основной путь. Новых экранов фронта нет.

---

## Связи

- **parties** — depositor на товаре и виртуальном складе.
- **documents** — задание и движение могут ссылаться на документ.
- **orders** — inbound порождает задание приёмки, outbound — отбор (FEFO).
- **accounts** — `assignee_id` на задании; `moved_by_id` на движении.

Остаток менять только через `StockService`. Роуты склада берут сервисы из `warehouse/deps.py`.

---

## Состояние

Этап 1 (DI склада) закрыт: роуты без `*Repository` и без `Services`.  
Этап 2 закрыт: unique остатка, LPN обязателен, `moved_at` на движении, pytest гонки.  
Этап 3 закрыт: inbound → приёмка → остаток+; outbound → FEFO → остаток−. Pytest в `tests/warehouse/test_receiving.py` и `test_picking.py`.

Журнал `StockMovement` без отдельного REST. Список товаров фильтруется query `depositor_id`, не `DataScope`. Generic Task CRUD не удалён.
