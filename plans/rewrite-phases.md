# План догонки lms_fastapi до WMS_01

Каркас нового проекта оставляем. Из старого переносим **поведение склада и тесты**, не `views.py` и не signals.

Не начинать следующий этап, пока не выполнен критерий текущего. Ширину CRUD (новые EntityList, тарифы, уведомления) не наращивать до конца этапа 3.

Источник истины по слоям: `ARCHITECTURE.md`.
Источник истины по моделям: `docs/09_models_improvements.md` (подмешивать в этапы 2–3, не отдельным «рефакторингом всего Base»).

**Очередь работ для нескольких чатов:** `plans/STATUS.md`. Спека не дублирует статусы — чат берёт задачу только там.

Код-донор: `/home/rustam/Data/projects/WMS_01`.

---

## Этап 0. Стоп и расчистка

**Цель.** Перестать расползаться вширь. Убрать то, что мешает читать склад.

**Работы**

- Удалить `app/parties/repository copy.py`.
- Подключить `app/files/routes.py` к `api_router` либо убрать Files с фронта.
- Зафиксировать: новые справочники и экраны не добавляем, пока не закрыт этап 3.
- Не чинить «все роуты сразу». Parties уже на `get_service` — это образец только для warehouse.

**Готово, когда** нет мёртвых дублей, files не 404, в git не появляется новый CRUD-модуль.

Статус: дубль удалён, files на `/api/v1/files`, `ClientService.get_or_create` для импорта есть. Заморозка CRUD — до конца этапа 3.

---

## Этап 1. DI только на контуре склада

**Цель.** Следующие сервисы склада писать сразу правильно. Не рефакторить весь API.

**Работы**

- `app/api/v1/warehouse/deps.py`: `get_stock_service`, `get_task_service`, `get_product_service`, … .
- Роуты `stock.py`, `tasks.py`, `products.py`, `topology.py` — только `Depends(get_*_service)`. Запрет `services.product._repo._s` и `Repository(services.session)`.
- Topology / группы / упаковки — через свои сервисы, даже тонкие.
- `ServiceContainer` не трогать у delivery/accounts, пока не дойдём до них (этап 7).

**Готово, когда** в `app/api/v1/warehouse/routes/` нет импорта `*Repository` и нет `Services`.

---

## Этап 2. Остаток как инвариант

**Цель.** Два параллельных прихода не создают две строки. Движение — журнал, баланс — снимок. Пишет только `StockService`.

**Взять из WMS_01**

- `warehouse_orders/models.py` — `StockMovement`, `StockBalance`, unique composite.
- Тесты остатка (гонка, ключ LPN, remove ниже нуля, move). Sentinel «без паллеты» **не брать**: у нас LPN обязателен, без `id=0` и без `COALESCE`.

**Не брать:** `warehouse_orders/signals.py`, `stock_balance_key.py` / `normalize_pallet_id`.

**Работы**

- Unique на `warehouse_stock_balance`: `(product_id, location_id, batch_id, lpn_id)`, колонка `lpn_id` NOT NULL. Без LPN — 400.
- `moved_at` и `moved_by_id` на `StockMovement` (биллинг и история не от `created_at`).
- Связь движения со строкой задания (`task_line_id` на `warehouse_task_line`).
- `StockService` — единственный writer баланса и движения, в одной транзакции, `FOR UPDATE` как сейчас.
- `get_available_quantity` не сканирует `list_all()` в Python.
- Pytest: гонка двух add, два LPN, add без LPN = ошибка, remove ниже нуля, move.

**Готово, когда** тесты ключа зелёные; в БД unique есть; ни один роут/импорт не делает `session.add(StockBalance)`.

---

## Этап 3. Приёмка и отбор

**Цель.** Склад исполняет заказ, а не хранит CRUD задания.

**Взять из WMS_01**

- `receive_line_pc` и TSD-скан приёмки — правила, не HTML.
- `ReceivingDiscrepancy`, отмена приёмки / реверс движения.
- `picking_planning_service.plan_picking_task_lines` (FEFO).
- Не склеивать приёмку и отбор в один сервис, даже если таблица `Task` общая.

**Работы**

- Воркфлоу по `task_type`: receiving / picking (movement и inventory — этап 6).
- Приёмка: скан/ручной ввод → факт, расхождение план/факт, закрытие, сторно.
- Отбор: планирование строк по FEFO (`expiry` с партии), резерв, закрытие → `remove`/`unreserve`.
- Встроить `PlacementService` в приёмку или удалить, если не используется.
- Заказы/документы: создание задания из inbound/outbound, а не «создай Task руками».
- `TaskLine.plan_qty`/`fact_qty` сейчас `Integer` — согласовать с `Numeric` остатка.

**Готово, когда** сценарий «inbound → задание приёмки → остаток вырос» и «outbound → план FEFO → остаток списан» проходит тестами без ручного `add_stock` из роута.

---

## Этап 4. Обмен с поклажедателем

**Цель.** Импорт не падает; партнёр получает ответные XML.

**Взять из WMS_01**

- `ZilandiXMLGenerator` (`pordrsp`, `ordrsp`, `desadv`, `recadv`).
- `DepositorWarehouseMapping` и нормализация LOC (ведущие нули).
- Флаги `*_exported` на заказе — поля в новом уже есть, дописать запись.

**Работы**

- `get_or_create` у клиента/адреса (сейчас `IntegrationService` зовёт методы, которых нет).
- Парсер оставить; добавить генерацию и выгрузку FTP.
- Маппинг склада поклажедателя.
- Фильтр списков по `User.depositor_ids` (иначе 3PL дырявый ещё до портала).
- Не подключать второй геокодер. DaData только если реально заменяет прод-Яндекс.

**Готово, когда** PORDER → заказ+документ; после приёмки уходит recadv/pordrsp; пользователь поклажедателя не видит чужие заказы.

---

## Этап 5. Пол: TSD API

**Цель.** Оператор на ТСД принимает и отбирает без админ-CRUD.

**Взять из WMS_01:** контракт `tsd/api/views.py` (login, claim, scan, assign pallet/LPN, complete). UI PWA не копировать.

**Работы**

- `/api/v1/tsd/...` на тех же сервисах этапа 3.
- JWT уже есть — отдельный короткий TTL/claim как в старом, если нужно.
- Минимальный фронт скана или PWA — после стабильного API.

**Готово, когда** приёмка и отбор проходятся только TSD-эндпоинтами (тест или ручной чеклист).

---

## Этап 6. Инвентаризация и перемещения

**Цель.** Закрыть дыры контура склада.

**Взять из WMS_01:** `InventoryDocument` dry-run → post; `MovementDocument`.

**Работы**

- Инвентаризация: план с остатка, ввод факта, прогон без записи, проводка через `StockService`.
- Перемещение ячейка→ячейка / LPN тем же сервисом, что `move_stock`.

**Готово, когда** dry-run не меняет баланс, post сходится с журналом движений.

---

## Этап 7. Добить слои на остальном API

**Цель.** Весь HTTP как warehouse после этапа 1.

**Работы**

- Удалить `ServiceContainer`.
- `app/api/v1/{feature}/deps.py` для orders, delivery, documents, accounts, integration.
- Остальные репозитории на `BaseRepository`.
- Сервисы бросают `NotFoundError` / `ConflictError` / `BadRequestError`, не `ValueError`.
- `database.py` → `infrastructure`; аудит не из `core/middleware` в модель напрямую.

**Готово, когда** список отклонений в `ARCHITECTURE.md` пуст (кроме сознательно отложенного).

---

## Этап 8. Деньги и бумаги (не блокер запуска склада)

Порядок внутри этапа — по боли прода:

1. Биллинг кг-дни / паллето-дни — `reports/services/billing.py`, дата = `moved_at`.
2. MX-1 / MX-3 / ТОРГ-2 — генераторы из `orders/services`, не views.
3. Паспорт LPN / печать — после стабильного LPN на приёмке.
4. Портал поклажедателя — поверх фильтра этапа 4.
5. Диадок — последним.

Отчёты на фронте не рисовать, пока нет сервисного расчёта.

---

## Вне скоупа навсегда

- Жирные Django views и signals как образец.
- Связи без FK.
- Порт 244 шаблонов.
- Внутренний тудушник `tasks.Task` из старого.
- Excel REST «как в README» старого (там заглушка).
- Новый геокодер без решения, какой был в проде.
