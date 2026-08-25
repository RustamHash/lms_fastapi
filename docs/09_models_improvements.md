# Модели: анализ и советы по улучшению

Документ только про ORM-модели (`app/*/models`, `app/files/models.py`, `app/infrastructure/orm_base.py`). Сервисы и API не трогаем, кроме случаев, где модель уже ломает целостность данных.

---

## 1. Что есть сейчас

Около 50 таблиц, все наследуют `Base` с полями:

`id`, `is_active`, `created_at`, `updated_at`, `created_by_id`, `updated_by_id`, `is_deleted`, `deleted_at`, `deleted_by_id`.

| Модуль | Таблицы |
|--------|---------|
| accounts | user, role, user_roles, audit, user_settings, user_table_settings, user_list_presets, user_depositor |
| parties | address, raw_address, delivery_zone, legal_entity, depositor, keeper, carrier, client, contract, tariff_document, tariff |
| warehouse | warehouse, virtual_warehouse, zone, row, location, product_group, product, package, batch, lpn, stock_balance, stock_movement, task, task_line, product_location |
| orders | inbound, inbound_line, outbound, outbound_line, return, return_line |
| documents | document, document_line |
| delivery | order, deviation, driver, vehicle, route, route_line |
| integration | profile, log, error |
| notifications | notification, rule |
| files | files |

Связи в целом читаемые. Ниже — разрывы, из-за которых склад и 3PL начнут врать в данных, как только вырастет нагрузка или появятся два одинаковых импорта.

---

## 2. Сквозные проблемы Base

### 2.1. Один `Base` на все сущности

**Сейчас.** Журнал аудита, движения остатков, лог импорта и уведомления получают `is_active`, `is_deleted` и девять audit-полей так же, как справочник клиентов.

**Зачем менять.** Soft delete на append-only логе бессмысленен: «удалённое движение» ломает сверку остатка. У `Audit` поле `is_active` не имеет предметного смысла. Лишние колонки и индексы на больших таблицах (`stock_movement`, `accounts_audit`) дорожают и путают запросы.

**Что даёт.** Разделить миксины:

- `IdMixin` — `id`
- `TimestampMixin` — `created_at` / `updated_at`
- `AuditUserMixin` — `created_by_id` / `updated_by_id`
- `SoftDeleteMixin` — `is_deleted` / `deleted_at` / `deleted_by_id`
- `ActiveMixin` — `is_active`

Справочники: все миксины. Документы и заказы: без обязательного `is_active`, либо оставить. Логи (`Audit`, `StockMovement`, `IntegrationLog`, `IntegrationError`): только id + timestamps + who. Остаток (`StockBalance`): без soft delete — нулевая строка удаляется или остаётся с `quantity = 0`.

### 2.2. Soft delete конфликтует с UNIQUE

**Сейчас.** Unique живёт в БД: `(depositor_id, external_id)` у товара, `(depositor_id, number)` у заказа, `lpn.number`, `document_number`. `is_deleted` в эти ключи не входит.

**Зачем.** После soft delete товара с кодом `SKU-1` нельзя завести новый `SKU-1` у того же поклажедателя — unique всё ещё занят «удалённой» строкой. То же для заказов, LPN, договоров.

**Что даёт.** Частичный уникальный индекс PostgreSQL:

```sql
CREATE UNIQUE INDEX uq_product_depositor_external_alive
  ON warehouse_product (depositor_id, external_id)
  WHERE is_deleted = false;
```

Можно повторно использовать код после удаления, не теряя историю. Альтернатива — суррогат `deleted_at` в ключе, хуже для запросов.

### 2.3. Python `default` без `server_default`

**Сейчас.** Почти все `default=""` / `default=False` / `default=dict` заданы только в ORM. В `Base` для флагов есть `server_default`. У большинства колонок заказов, склада, доставки — нет. Исключение: несколько полей `OutboundOrder` (`is_edo`, `address_comment`, …).

**Зачем.** Сырой SQL, Alembic `op.execute`, Celery-сессия без конструктора модели, `COPY` — вставляют NULL или падают. Два пути записи в одну таблицу начинают расходиться.

**Что даёт.** Для NOT NULL колонок всегда пара: `default=...` (Python) + `server_default=...` (БД). Булевы — `'false'`/`'true'`, строки — `''`, JSONB — `'{}'::jsonb`. Инвариант держит база, не только ORM.

### 2.4. Статусы и типы — свободные строки

**Сейчас.** Enum есть в `app/core/statuses.py` (`OrderStatus`, `DocumentStatus`, `TaskStatus`, `DeliveryStatus`), в колонках — `String(20|30|50)` с Python-default. В БД можно записать `"foo"`. То же для `task_type`, `zone_type`, `document_type`, `direction`, `contract_type`, `return_type`.

**Зачем.** Опечатка в импорте или PATCH из UI создаёт заказ в статусе, которого нет на фронте и в переходах. Отчёты по статусу молча теряют строки.

**Что даёт.** `sqlalchemy.Enum(..., native_enum=False)` или `CheckConstraint("status IN (...)")`. Нативная PG ENUM неудобна в миграциях; строка + CHECK достаточно. Невалидное значение отсекается на INSERT/UPDATE, а не в отчёте через месяц.

`User.has_permission` и `parent_role` к колонкам не относятся, но `Role.permissions` JSONB без схемы — та же дыра: в JSON можно положить что угодно. Имеет смысл JSON Schema или отдельная таблица `role_permission(role_id, entity, action)`.

### 2.5. `lazy="selectin"` на моделях

**Сейчас.** На `User.roles`, `Address.delivery_zone`, `Address.raw_addresses`, `DeliveryZone.addresses`, `LegalEntity.*_address`, `Client.*`, `Contract.tariff_documents`, `TariffDocument.tariffs`, заказах, доставке — `lazy="selectin"`.

**Зачем.** Любой `list_all()` зоны доставки подтянет **все** адреса зоны. Список договоров — все тарифные документы и тарифы. Это не настройка модели, это скрытый JOIN на каждый SELECT.

**Что даёт.** На модели оставить `lazy="selectin"` только для обязательных маленьких связей (например `User.roles` — без ролей пользователь бесполезен). Коллекции (`addresses`, `tariffs`, `lines`) — default `select` + явный `selectinload` в репозитории list/detail. Списки перестают раздуваться, деталка остаётся удобной.

### 2.6. FK без `ondelete`

**Сейчас.** Почти все `ForeignKey("...")` без `ondelete`. PostgreSQL по умолчанию `RESTRICT`/`NO ACTION`.

**Зачем.** Удаление (даже hard) склада с ячейками, заказа со строками, маршрута со стоп-поинтами — либо падает, либо требует ручного порядка DELETE. `user_roles` при удалении роли оставит висячие пары или заблокирует DELETE. `NotificationRule.role_code → accounts_role.code` при смене кода роли ломает правила.

**Что даёт.** Политика по типу связи:

| Связь | ondelete | Почему |
|-------|----------|--------|
| Строки заказа / документа / задания / маршрута | `CASCADE` | Строка без шапки не существует |
| M2M `user_roles` | `CASCADE` | Связь, не сущность |
| Справочник (товар, ячейка, клиент) с операционных таблиц | `RESTRICT` | Нельзя снести товар с остатком |
| Опциональные FK (`assignee_id`, `file_id`) | `SET NULL` | Исполнитель уволился — задание остаётся |

Для soft delete `ondelete` срабатывает реже, но hard-cleanup, тесты и `clear_orders.py` начнут работать предсказуемо.

### 2.7. Имена таблиц

**Сейчас.** Префикс модуля: `accounts_*`, `parties_*`, `warehouse_*`, `orders_*`, `documents_*`, `notifications_*`. Исключения: `delivery_order` (не `delivery_delivery_order` — нормально), но нет префикса `delivery_` единообразно? Есть `delivery_driver`, `delivery_order`. `files` и `integration_*` без доменного префикса уровня `app`. `warehouse_warehouse` — тавтология.

**Зачем.** Мелочь для запросов и прав в PG. `files` легко пересекается с чужой схемой.

**Что даёт.** Не переименовывать боевые таблицы без нужды. Для новых: `{module}_{entity}` (`files_file`, `integration_profile` уже ок). `warehouse_warehouse` оставить — миграция дороже выгоды.

### 2.8. Модель ≠ миграции unique

**Сейчас.** Миграция `20260822014929` вешает unique на `documents_document.document_number`, `warehouse_product (depositor_id, external_id)`, `warehouse_lpn.number`, `parties_contract.number`, `delivery_order.number`, `delivery_route.number`, `warehouse_warehouse.name`, `warehouse_zone.name`. В `__table_args__` моделей этого нет (кроме заказов inbound/outbound).

**Зачем.** Следующий `alembic revision --autogenerate` предложит **снять** эти ограничения. Новый разработчик смотрит модель и думает, что номер документа не уникален.

**Что даёт.** Перенести все unique в `__table_args__` моделей. Alembic перестаёт врать, код — источник правды.

Часть этих unique при этом **неверна по смыслу** — см. разделы documents/warehouse/parties ниже.

---

## 3. Связи между агрегатами (дыры WMS)

Это главная предметная проблема моделей, не стиль кода.

```
Inbound/OutboundOrder  ──?──  Document  ──FK──  Task
         │                      │
         └── DeliveryOrder ─────┘
```

**Сейчас.**

- `Document` не ссылается на inbound/outbound. Связь только через совпадение `document_number` и создание в `IntegrationService`.
- `Task` ссылается на `document_id`, не на заказ.
- `DeliveryOrder` имеет и `document_id`, и `outbound_order_id` — хорошо.
- `OutboundOrder.delivery_status` дублирует `DeliveryOrder.status`.
- `StockMovement` знает `document_id`, не знает `task_id` / `task_line_id`.
- `ReturnOrder` знает оба заказа, не знает документ возврата.

**Зачем.** Нельзя надёжно открыть «заказ → документы → задания → движения». Деталка исходящего заказа на фронте уже ждёт `documents` и `tasks` — в модели их нет. Сверка «почему остаток ушёл» упирается в эвристики по номеру.

**Что даёт.** Явные FK:

```text
documents_document
  inbound_order_id  FK orders_inbound  NULL
  outbound_order_id FK orders_outbound NULL
  return_order_id   FK orders_return   NULL
  CHECK: ровно один из трёх (или ни одного для перемещения/инвентаризации)

warehouse_task
  как сейчас document_id + опционально те же order FK для выборок

warehouse_stock_movement
  task_id, task_line_id  NULL
```

Один заказ — несколько документов (недогруз, довоз) остаются возможны. Отчёт «движения по заказу» — JOIN, не парсинг номера.

Убрать `OutboundOrder.delivery_status` либо сделать generated/кэшем с правилом обновления только из `DeliveryOrder`. Два источника правды по статусу доставки разъедутся на первом же ручном PATCH.

---

## 4. Модуль accounts

### User

- `email` с `default=""` и без unique. Два пользователя с пустым email ок, два с одним рабочим email — дыра для восстановления доступа. **Совет:** `nullable=True` + unique на непустых (`WHERE email <> ''`) или требовать email.
- `phone` — строка без нормализации. Не модель, но колонки `String(20)` режет `+7 (999) ...`.
- `extra_permissions` JSONB — ок как override, но без проверки ключей. **Совет:** те же entity/action, что у роли; иначе UI нарисует право, бэкенд его не поймёт.
- Методы `has_permission` на ORM-классе. **Совет:** оставить пока (удобно), но `parent_role` не обходится — поле в модели врёт. Либо рекурсия/замыкание в проверке, либо удалить `parent_role_id`. Мёртвое поле хуже отсутствия: админ думает, что «кладовщик наследует просмотр».
- Нет `relationship` на `UserDepositor`. Скоуп 3PL не читается с пользователя. **Совет:** `depositors = relationship(..., secondary=...)` или `user_depositors`. Иначе изоляция данных только в забывчивом коде сервиса.

### Role / user_roles

- `user_roles` — голый `Table` без timestamps и без `ondelete=CASCADE`. Нормально для M2M. CASCADE обязателен.
- `permissions: dict[str, Any]` — слишком широко. **Совет:** `dict[str, list[str]]` как у User.

### Audit

- Наследует soft delete — убрать (п. 2.1).
- `entity_id: String(36)` при том что PK сущностей — int. UUID заказа сюда влезет, int тоже. **Совет:** два поля (`entity_int_id`, `entity_uuid`) или всегда строка, но индекс `(entity_type, entity_id)` — журнал без индекса по сущности нельзя фильтровать.
- Нет индекса `(user_id, created_at)`, `(entity_type, entity_id)`. Таблица только растёт.

### UserSettings / TableSettings / Preset

- Выглядят здраво: unique `(user_id, table_id)`, пресет `(user_id, table_id, name)`.
- `is_default` на пресете не уникален: два default на одну таблицу возможны. **Совет:** частичный unique `(user_id, table_id) WHERE is_default`.
- `page_size` в настройках таблицы есть, API списков пагинации нет — поле модели опережает код. Оставить, пригодится.

### UserDepositor

- Нет `is_default` / роли в рамках поклажедателя. Пока достаточно unique пары. Добавить relationship в обе стороны.

---

## 5. Модуль parties

### Address / RawAddress

- `RawAddress.hash` unique — хорошо, идемпотентность ввода.
- У `Address` нет unique по `fias_id` (где не пустой) и по нормализованному `full_address`. `get_or_create` ищет в Python — гонка двух импортов создаст два адреса на один FIAS. **Совет:** `UNIQUE (fias_id) WHERE fias_id <> ''`.
- `full_address` Text без индекса — поиск по подстроке всё равно seq scan; для exact match после нормализации хватит hash/fias.
- `DeliveryZone.addresses` selectin — убрать (п. 2.5). Иначе карточка зоны = вся Москва.
- Координаты `Numeric(9, 6)` — ок для DaData. Для геозон позже понадобится PostGIS; не закладывать сейчас, но `Numeric` лучше `float`.

### LegalEntity

- `inn` не уникален. В РФ ИНН юрлица уникален (кроме филиалов с разным КПП). **Совет:** unique `(inn, kpp)` где inn не пустой. Иначе два «ООО Ромашка» с одним ИНН — разные поклажедатели на одно юрлицо по смыслу бизнеса.
- Нет обратных связей на Depositor/Keeper/Carrier. OneToOne уже через unique `legal_entity_id` у ролей. **Совет:** `depositor = relationship(uselist=False)` для навигации.

### Depositor / Keeper / Carrier

- Три таблицы 1:1 к юрлицу — правильный паттерн ролей (одно юрлицо может быть и поклажедателем, и перевозчиком).
- `Depositor.code` без unique. Импорт ищит по id, UI — по коду. **Совет:** unique code, хотя бы `WHERE code <> ''`.
- Keeper/Carrier — пустые оболочки (только FK). Нормально, пока нет лицензии/договора на роль. Не плодить поля «на вырост».

### Client

- Unique `(depositor_id, code, delivery_address_id)` — осознанно: один код клиента, разные адреса доставки = разные карточки. Postgres: `NULL` в unique **не равны**, два клиента с одним code и `delivery_address_id IS NULL` пройдут. **Совет:** `delivery_address_id` NOT NULL для этой схемы, либо частичный unique.
- `inn`/`kpp`/`legal_name` дублируют LegalEntity. Клиент 3PL часто не ваше юрлицо — дублирование ок. Связь на `legal_entity_id` опционально, когда клиент — тоже юрлицо в справочнике.

### Contract / Tariff

- Unique на `contract.number` **глобально** (миграция) — два договора разных пар юрлиц с номером «1» невозможны. **Совет:** unique `(customer_id, executor_id, number)` или `(executor_id, number)`.
- `terms: JSON` вместо JSONB. **Совет:** JSONB — индексы, `?` операторы, единообразие с остальным проектом.
- `contract_type`, `status` — строки. CHECK или enum.
- `TariffDocument.file_id` → `files.id` без `ondelete=SET NULL`.
- Нет unique `(contract_id, number)` у тарифного документа.
- НДС `vat_rate: String(10)` — лучше `Numeric(4, 2)` или enum `0/10/20/none`. Строка «20%» vs «20» сломает расчёт.

---

## 6. Модуль warehouse (критично)

### Topology

- Unique `warehouse.name` глобально — два склада «Основной» нельзя. Обычно ок для одной компании.
- Unique `warehouse_zone.name` **глобально** — ошибка. Зона «Отбор» должна быть на каждом складе. **Совет:** unique `(warehouse_id, name)`.
- Нет unique `(warehouse_id, code)` у VirtualWarehouse — импорт `get_or_create` по code, гонка создаст дубли, заказы разъедутся по «двум» виртуальным складам.
- Нет unique `(zone_id, code)` у Row, `(row_id, position, level)` у Location. Две ячейки в одном месте — остаток непонятно куда класть.
- `Location.max_weight` / `max_volume` — `float`. Остальной вес — `Numeric`. Сравнение float с Decimal даёт сюрпризы. **Совет:** `Numeric(12, 3)` как везде.
- Нет `location_type` (отбор / хранение / приёмка / брак). FEFO в `PlacementService` вынужден угадывать по `ProductLocation` и «первой свободной». Тип зоны (`zone_type`) есть, типа ячейки нет — для WMS ячейка важнее зоны.
- Нет barcode/QR ячейки (`Location.code`). Терминал сбора не к чему привязать, кроме id.

### Product / Package / Batch

- Unique `(depositor_id, external_id)` в БД, не в модели — перенести (п. 2.8).
- `volume` NOT NULL. Импорт подставляет 0. Лучше `nullable=True`: 0 лжёт («объём известен и нулевой»).
- Штрихкод живёт на `Package`, не на `Product`. Это правильно (разные EAN на коробку и штуку). Unique `Package.barcode` **глобально** — один EAN не может быть у двух поклажедателей. В 3PL одинаковые EAN у разных owners бывают. **Совет:** unique `(barcode)` WHERE barcode IS NOT NULL оставить только если EAN глобально уникален в вашем контуре; иначе `(product.depositor через join)` или barcode без unique + индекс.
- Нет unique «одна базовая упаковка на товар»: два `is_base_unit=True`. **Совет:** частичный unique `(product_id) WHERE is_base_unit`.
- `Batch`: нет unique `(product_id, batch_number)`. Две партии «A-1» у одного товара — FEFO и остатки ветвятся. Обязательный unique.
- Нет `depositor_id` на Batch (он через product) — нормально.

### LPN

- Unique number — хорошо.
- Нет `location_id`, нет `warehouse_id`. Паллета «где стоит» выводится только через `StockBalance`. Если LPN пустой — место неизвестно. **Совет:** опциональный `current_location_id` (кэш) или смириться и всегда смотреть баланс. Для ТСД удобен кэш.
- `status` строка без CHECK (`created`, `in_stock`, `shipped`, …).

### StockBalance — самое опасное место

**Сделано (этап 2).** Unique `(product_id, location_id, batch_id, lpn_id)`, `lpn_id` NOT NULL (без COALESCE и без sentinel `0`). CHECK quantity/reserved, индекс `(product_id, location_id)`. `StockService` — единственный writer; гонка insert ловится unique.

Осталось из этого пункта: индекс `(batch_id)` для FEFO; unique не учитывает `is_deleted` (soft delete на остатке лучше убрать, п. 2.1).

### StockMovement

- Append-only: без soft delete (п. 2.1) — ещё не делали.
- `moved_at` / `moved_by_id` / `task_line_id` — **сделано** (этап 2). Биллинг смотрит `moved_at`.
- Нет пары from/to на одно перемещение: `move_stock` пишет два движения in/out. Это нормальная схема двойной записи. Тогда нужен `operation_id` (UUID), чтобы связать пару, иначе отчёт «перемещения» клеит по времени.
- `direction` — CHECK `IN ('in', 'out')` (и `'adjust'`, если инвентаризация не через in/out).

### Task / TaskLine

- `plan_qty` / `fact_qty` — `Integer`. У заказа и документа — `Numeric(10|20, 3)`. Вес в кг и дробные штуки (кг, литры) на задании округлятся. **Совет:** тот же `Numeric(20, 3)` везде. Иначе complete_line не совпадёт с document_line.
- Нет unique `(task_id, document_line_id)` — две строки задания на одну строку документа.
- `cascade="all, delete-orphan"` на lines при soft delete шапки **не срабатывает** (строка не DELETE). Для soft delete каскад надо делать в сервисе; в модели каскад только для hard delete. Не полагаться на ORM cascade как на бизнес-правило.
- Нет `warehouse_id` на Task — только через документ. Выборка «задания склада» = JOIN.

### ProductLocation

- Нет unique `(product_id, location_id)`. FEFO обойдёт дубли как две ячейки. Unique обязателен.
- Нет признака приоритета / min-max на полке. Можно позже.

---

## 7. Модуль orders

### Inbound / Outbound

- Unique `(depositor_id, number)` — правильно для 3PL (у каждого поклажедателя своя нумерация). Держать и в модели, и как частичный индекс с `is_deleted = false`.
- `InboundOrder` импортирует `Client`, `Warehouse` на уровне модуля — лишняя связь пакета. Достаточно quoted `"Client"` в relationship.
- Денормализация outbound: `customer_code`, `customer_name`, `delivery_address_name` + FK `client_id`. Имеет смысл как снимок на момент заказа (клиент переименуется — заказ не должен поехать). **Зафиксировать правилом:** поля снимка заполняются при создании и не редактируются вслед за клиентом, либо убрать и всегда JOIN. Сейчас оба пути открыты — расхождение гарантировано.
- `delivery_contact` и `shipping_contact` — два контакта с похожим смыслом. **Совет:** одно поле или явно «контакт отгрузки» vs «контакт на адресе».
- `uuid` для QR — хорошо. Тип `String(36)` + `default=lambda`. Лучше `Uuid` / `PGUUID`, `server_default=gen_random_uuid()`.
- `total_quantity: Integer` vs строки `Numeric` — сумма будет врать на дробях. Numeric или считать агрегатом, не колонкой. Колонка-кэш без триггера/сервиса разъедется.
- `document_number` на outbound дублирует Document. Либо FK на документ, либо убрать.
- Нет FK на `delivery_address_id` — только строка `delivery_address_name`. Зона `zone_id` есть, адрес как сущность — нет. Маршрут и повторный импорт не попадут в тот же Address. **Совет:** `delivery_address_id` FK + строка как snapshot.

### Lines

- Нет unique `(order_id, product_id, batch_number)` — дубли строк с одним SKU обычны (две партии), так что unique по product нельзя. Ок без unique, но нужен `line_no` для стабильного порядка и сверки с XML `ITEM/ID`.
- `serial_numbers` JSONB list — ок до отдельной таблицы марок. Когда `is_marked` станет обязательным, JSON перестанет хватать (поиск марки, уникальность). Не делать таблицу заранее, помнить лимит.
- `product_id` nullable. Строка без товара — импорт «не нашли SKU». Имеет смысл `external_id` на строке заказа, чтобы не терять исходный код, если Product не создался.

### ReturnOrder

- Нет собственного `number` / unique. Список возвратов нельзя идемпотентно импортировать.
- `status` / `return_type` — свободные строки, не в `core/statuses.py`.
- Нет связи с Document. Возврат на склад без приходного документа в модели не отражён (есть `inbound_order_id` — хорошо, документа нет).

---

## 8. Модуль documents

- Unique `document_number` **глобально** — у двух складов/поклажедателей номер «123» столкнётся. **Совет:** `(warehouse_id, document_type, document_number)` или `(virtual_warehouse_id, document_number)`.
- Нет `depositor_id`. Изоляция 3PL через `virtual_warehouse` (nullable!). Документ без VW — общий костёл. **Совет:** `depositor_id` NOT NULL для receipt/shipment.
- Нет FK на заказ (раздел 3).
- `warehouse_id` NOT NULL, relationship помечен как `Warehouse | None` — противоречие типов.
- `processed_quantity` на строке без CHECK `<= quantity`.
- Каскад lines — см. Task: при soft delete шапки строки живы. Либо не soft-delete документы с движениями (запрет в сервисе + статус cancelled), либо каскадный soft delete в одном месте.

---

## 9. Модуль delivery

- Unique `delivery_order.number` глобально — лучше `(date, number)` или префикс по складу. Иначе два дня подряд «М-1» нельзя, или наоборот нельзя два «М-1» в один день — зависит от бизнеса. Зафиксировать правило в unique.
- `parent_id` (дробление заявки) без `remote_side` relationship. Добавить `parent` / `children`.
- Нет unique `outbound_order_id`: два DeliveryOrder на один исходящий заказ возможны (довоз — ок). Если не ок — unique.
- `Vehicle.number` (госномер) без unique. Две карточки одной машины.
- `Route.number` unique глобально — см. заказы доставки.
- `RouteLine.order` — имя колонки совпадает с reserved SQL и с доменом Order. **Совет:** `stop_no` / `sequence`. Меньше боли в сыром SQL.
- Нет unique `(route_id, delivery_order_id)` — один заказ дважды в маршруте. Нет unique `(route_id, order)` — два стопа с порядком 1.
- `Driver.phone` без unique.

---

## 10. Integration / notifications / files

### IntegrationProfile / Log / Error

- `config` JSONB с паролем FTP. Это не колонка «улучшить тип», это секрет в БД. **Совет:** вынести секреты в vault/env, в config — host/path; или хотя бы не отдавать password в API Read-схеме (это уже не модель, но колонка провоцирует утечку).
- `task_id` без unique — два лога на одну Celery-задачу. Unique обязателен.
- `messages`/`errors` JSONB-массивы растут бесконечно на одном логе. Либо таблица `IntegrationError` (она уже есть!) и не дублировать текст в JSON лога, либо ограничить размер. Сейчас и JSON, и таблица error — два канала.
- `File` импортируется в `integration_profile.py` ради type? Только `file_id` на логе. Неиспользуемый import `File` в модели профиля — убрать.

### Notification

- `sent_at` / `read_at` — `String(50)`. Должно быть `DateTime(timezone=True)`. Иначе сортировка «непрочитанные» и TTL — строковое сравнение.
- `status` pending/read — ок, CHECK.

### NotificationRule

- Повторно объявлен `is_active` (уже в Base). Лишнее переопределение, другой comment. Убрать, пользоваться Base.
- `role_code` FK на `accounts_role.code`, не на `id`. Смена code ломает FK или запрещает rename. **Совет:** `role_id` FK на `accounts_role.id`.

### File

- Таблица `files` без префикса.
- `uploaded_by_id` **без ForeignKey**. Сирота, нет целостности. Должен быть `FK accounts_user.id`, `ondelete=SET NULL`. Дублирует `created_by_id` из Base — одно поле лишнее.
- Нет `content_hash` — дедуп загрузок и проверка целостности.

---

## 11. Согласованность типов (сводка)

Одинаковый смысл — разные типы. Это ломает сравнения, суммы и FEFO.

| Смысл | Где как | Как надо |
|-------|---------|----------|
| Количество | OrderLine Numeric(10,3); DocumentLine Numeric(20,3); TaskLine **Integer**; Deviation **int** «мест» | Количество товара — везде Numeric(20,3). Места — отдельная колонка Integer |
| Вес | Product Numeric; Location **float**; Vehicle Numeric | Numeric |
| Деньги | Tariff Numeric(12,2); Product.price Numeric(12,2) | Ок, не смешивать с количеством |
| UUID | Outbound String(36); IntegrationLog String(36) | `Uuid` + server_default |
| Время события | Notification **String**; остальные DateTime | DateTime TZ |
| JSON | Contract **JSON**; остальные JSONB | JSONB |
| Статус | String разной длины, часть с Enum в Python | String + CHECK, одна длина (32 хватит) |

`Numeric(10,3)` vs `(20,3)` — выровнять в сторону 20,3 на операционных таблицах (остаток уже 20,3). Иначе сумма строк документа не влезет в строку заказа или наоборот.

---

## 12. Что можно не трогать

- Integer PK везде: для внутренней LMS проще UUID, менять поздно и незачем. UUID на outbound для QR — достаточно.
- Разделение Depositor/Keeper/Carrier: правильная модель ролей юрлица.
- RawAddress + hash: правильная идемпотентность ввода адреса.
- UserTableSettings / presets: нормальная модель UI state.
- Двойная запись StockMovement in/out: нормальная бухгалтерская схема, если появится `operation_id`.
- Snapshot ФИО клиента на заказе: нормально, если запретить «тихую» перезапись из карточки клиента.

---

## 13. Порядок внедрения (модели + миграции)

Не делать всё сразу. Каждый шаг — одна миграция и правка `__table_args__`, чтобы модель снова совпала с БД.

### Сначала (целостность склада, иначе данные уже гниют)

1. Unique остатка: LPN обязателен, `(product_id, location_id, batch_id, lpn_id)` + CHECK quantity/reserved — **сделано**.
2. Unique `(product_id, batch_number)` на партиях.
3. Unique `(product_id, location_id)` на ProductLocation.
4. Unique `(warehouse_id, code)` на VirtualWarehouse; `(warehouse_id, name)` на Zone вместо глобального имени; `(row_id, position, level)` на Location.
5. Выровнять TaskLine qty на Numeric(20,3).
6. Перенести существующие unique из «голой» миграции в модели.

### Потом (связи процесса)

7. FK Document → заказ (inbound/outbound/return).
8. `operation_id` на паре move; `task_line_id` на движении — **сделано**.
9. `delivery_address_id` на OutboundOrder; решить судьбу `delivery_status`.
10. Частичные unique `WHERE NOT is_deleted` на товарах и номерах заказов.

### Затем (гигиена)

11. Миксины вместо единого Base для логов.
12. CHECK на статусы/типы.
13. `server_default` на NOT NULL.
14. Снять `lazy="selectin"` с коллекций.
15. `ondelete` по таблице в разделе 2.6.
16. Notification DateTime; File FK; IntegrationLog.task_id unique; Vehicle.number unique.
17. Исправить заведомо широкие unique: zone name, contract number, document number.

После шага 1–4 имеет смысл скрипт дедупликации: найти двойные stock_balance / batch / location и слить quantity, иначе UNIQUE миграция не накатится.

---

## 14. Зачем это всё, одной фразой на блок

| Блок | Зачем | Что получите |
|------|--------|----------------|
| Unique остатка и партий | Запретить два баланса в одной ячейке | Остаток = сумма движений, FEFO не ветвится |
| Partial unique + soft delete | Удалять и заводить код заново | История жива, справочник не заблокирован |
| FK заказ ↔ документ ↔ задание ↔ движение | Собрать процесс в данных, не в импорте | Деталка заказа, аудит, отчёты без эвристик |
| Enum/CHECK статусов | Не хранить мусор | Отчёты и переходы статусов предсказуемы |
| Одинаковый Numeric | Не резать кг на задании | План/факт/документ сходятся |
| Миксины Base | Не soft-delete'ить журнал | Меньше колонок, честный append-only |
| Модель = БД unique | Autogenerate не снесёт ключи | Миграции безопасны |
| selectin только где нужно | Не грузить тарифы списком договоров | Списки остаются списками |
| Секреты и типы дат/UUID | Не врать схемой | Меньше багов на граничных значениях |

Модели сейчас описывают **справочники хорошо**, а **операционный контур склада — слабо** (остаток, связи заказа с документом, типы количеств). Улучшения выше — про инварианты в PostgreSQL: то, что нельзя сломать сервисом, гонкой или ручным SQL.
