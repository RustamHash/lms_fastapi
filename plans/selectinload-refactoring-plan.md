# План рефакторинга: selectinload для вложенных связей

## Цель
Заменить ленивую загрузку на `selectinload` во всех list- и detail-роутах.

## Принципы
1. **List-роуты** — `selectinload` для связей, которые отображаются в таблице (имя, номер, код)
2. **Detail-роуты** — `selectinload` для всех связей, которые отображаются на детальной странице
3. **Не подтягивать** лишние связи, если они не отображаются

---

## 1. Accounts

### Users
**List (`GET /users`):**
- `roles` — роли пользователя

**Detail (`GET /users/{id}`):**
- `roles` — роли
- `user_settings` — настройки
- `user_depositors` — привязки к поклажедателям

### Roles
**List (`GET /roles`):**
- без вложенных (все поля в самой таблице)

**Detail (`GET /roles/{id}`):**
- `users` — пользователи с этой ролью

### UserSettings
**List (`GET /user-settings`):**
- без вложенных

**Detail (`GET /user-settings/{id}`):**
- `user` — пользователь

### UserDepositor
**List (`GET /user-depositors`):**
- `user` — пользователь
- `depositor` — поклажедатель

---

## 2. Parties

### Addresses
**List (`GET /addresses/list`):**
- `delivery_zone` — зона доставки (для zone_name)

**Detail (`GET /addresses/{id}/detail`):**
- `delivery_zone` — зона
- `raw_addresses` — сырые адреса

### LegalEntities
**List (`GET /legal-entities`):**
- без вложенных

**Detail (`GET /legal-entities/{id}`):**
- `legal_address` — юр. адрес
- `actual_address` — факт. адрес

### Depositors
**List (`GET /depositors`):**
- `legal_entity` — юрлицо (для name)

**Detail (`GET /depositors/{id}`):**
- `legal_entity` — юрлицо

### Clients
**List (`GET /clients`):**
- `delivery_address` — адрес доставки
- `legal_address` — юр. адрес

**Detail (`GET /clients/{id}`):**
- `delivery_address` + `delivery_address.delivery_zone`
- `legal_address`
- `depositor`

### Contracts
**List (`GET /contracts`):**
- `customer` — заказчик (имя)
- `executor` — исполнитель (имя)

**Detail (`GET /contracts/{id}`):**
- `customer`
- `executor`
- `tariff_documents` — тарифные документы

### TariffDocuments
**List (`GET /tariff-documents`):**
- `contract` — договор

**Detail (`GET /tariff-documents/{id}`):**
- `contract`
- `tariffs` — тарифы

### Tariffs
**List (`GET /tariffs`):**
- `document` — тарифный документ

### Carriers / Keepers
**List:**
- `legal_entity` — юрлицо

### DeliveryZones
**List:**
- без вложенных

**Detail:**
- `addresses` — адреса в зоне

---

## 3. Warehouse

### Products
**List (`GET /products`):**
- `group` — группа товара

**Detail (`GET /products/{id}`):**
- `group`
- `depositor`
- `packages` — упаковки
- `batches` — партии

### Batches
**List (`GET /batches`):**
- `product` — товар

**Detail (`GET /batches/{id}`):**
- `product`

### LPNs
**List (`GET /lpns`):**
- без вложенных

**Detail (`GET /lpns/{id}`):**
- `stock_balances` — остатки

### Packages
**List (`GET /packages`):**
- `product` — товар

### ProductGroups
**List:**
- без вложенных

**Detail:**
- `products` — товары в группе

### ProductLocations
**List:**
- `product` — товар
- `location` — ячейка

### StockBalances
**List (`GET /stock`):**
- `product` — товар
- `location` — ячейка
- `lpn` — паллета
- `batch` — партия

### StockMovements
**List:**
- `product`
- `location`
- `batch`

### Tasks
**List (`GET /tasks/list`):**
- `document` — документ (номер)
- `assignee` — исполнитель (имя)

**Detail (`GET /tasks/{id}/detail`):**
- `document`
- `assignee`
- `lines` + `lines.product` + `lines.from_location` + `lines.to_location`

### Warehouses / Zones / Rows / Locations
**List:**
- `warehouse` (для zones)
- `zone` (для rows)
- `row` (для locations)

**Detail:**
- вложенные дочерние элементы (zones → rows → locations)

---

## 4. Orders

### InboundOrders
**List (`GET /inbound-orders/list`):**
- `depositor` + `depositor.legal_entity`
- `supplier` — поставщик
- `warehouse` — склад

**Detail (`GET /inbound-orders/{id}/detail`):**
- `depositor` + `legal_entity`
- `supplier`
- `warehouse`
- `lines` + `lines.product`

### OutboundOrders
**List (`GET /outbound-orders/list`):**
- `depositor` + `legal_entity`
- `client` + `client.delivery_address` + `delivery_zone`
- `warehouse`

**Detail (`GET /outbound-orders/{id}/detail`):**
- `depositor` + `legal_entity`
- `client` + `delivery_address` + `zone`
- `warehouse`
- `lines` + `lines.product` + `lines.location`

### ReturnOrders
**List:**
- `depositor`

**Detail:**
- `depositor`
- `lines` + `lines.product`

---

## 5. Documents

### Documents
**List (`GET /documents/list`):**
- `warehouse` — склад

**Detail (`GET /documents/{id}/detail`):**
- `warehouse`
- `virtual_warehouse`
- `contract`
- `lines` + `lines.product` + `lines.batch`

---

## 6. Delivery

### DeliveryOrders
**List (`GET /delivery/orders/list`):**
- `outbound_order` — исходящий заказ (номер)
- `route` — маршрут
- `route.driver` — водитель
- `route.vehicle` — автомобиль

**Detail (`GET /delivery/orders/{id}/detail`):**
- `outbound_order`
- `route` + `driver` + `vehicle`
- `document`
- `deviations`

### Drivers
**List:**
- `carrier` — перевозчик

### Vehicles
**List:**
- `carrier`

### Routes
**List:**
- `driver` — водитель
- `vehicle` — автомобиль

**Detail:**
- `driver`
- `vehicle`
- `lines` + `lines.delivery_order`

---

## 7. Integration

### Profiles
**List:**
- `depositor` — поклажедатель

### Logs
**List:**
- `profile` — профиль

---

## 8. Notifications

### Notifications
**List:**
- `user` — получатель

### NotificationRules
**List:**
- без вложенных

---

## Порядок реализации

1. ✅ **Documents** — наиболее используемые
2. ✅ **Orders (Inbound, Outbound, Return)**
3. ✅ **Delivery**
4. ✅ **Warehouse (Products, Tasks, Stock)**
5. ✅ **Parties (Addresses, Clients, Depositors)**
6. ✅ **Accounts (Users)**
7. ✅ **Integration / Notifications**

---

## Критерии приёмки

- [ ] Все list-роуты возвращают данные за ≤ 5 запросов к БД
- [ ] Все detail-роуты возвращают полные вложенные объекты
- [ ] Нет N+1 запросов
- [ ] Время ответа list ≤ 200 мс для 100 записей
- [ ] Время ответа detail ≤ 100 мс
