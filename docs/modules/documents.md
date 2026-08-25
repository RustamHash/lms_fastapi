# documents — складские документы

Документ — основание движения на складе (приход, отгрузка, перемещение, инвентаризация, корректировка). Отличается от заявки (`orders`): заявка — что хочет поклажедатель; документ — что проводит склад.

Код: `app/documents/`. HTTP: `app/api/v1/documents/`.

---

## Модели

**Document** (`documents_document`): `document_number`, даты, `document_type`, `warehouse_id`, опционально `virtual_warehouse_id`, `inbound_order_id` (PORDER), `contract_id`, `status`, `is_delivery`, `is_edo`.

Типы: `DocumentType` в `app/documents/document_types.py` — `receipt`, `shipment`, `movement`, `inventory`, `adjustment`.

Статусы: `DocumentStatus` — `draft`, `task_created`, `in_progress`, `completed`, `cancelled`.

**DocumentLine**: товар, партия, `quantity`, `processed_quantity`.

---

## Сервис

`DocumentService`: CRUD документа, `list_by_type`, `add_line` (qty > 0), `set_status`, `plan_fact` (строки = план, движения по `document_id` = факт, сверка `quantity` vs `processed_quantity`).

Не проводит остаток сам — это `StockService` / задания. Связь «заказ → документ → задание» в целевом контуре этапа 3.

События (задуманы): `document.created`, `document.status_changed` — см. `EventTypes`.

---

## API

`/api/v1/documents` — CRUD, строки, смена статуса.  
`GET /documents/{id}/plan-fact` — план/факт/сверка для карточки (право `view` на `documents`).  
RBAC: `documents`.

Карточка `/documents/:id`: шапка документа и вкладки **План** (строки), **Факт** (движения), **Расхождения** (`quantity` vs `processed_quantity`).

---

## Связи

- **warehouse** — склад, виртуальный склад, товар/партия в строках; `Task.document_id`, `StockMovement.document_id`.
- **parties** — договор.
- **orders** — `InboundExchangeService` создаёт inbound и документ с `inbound_order_id`. Outbound/return FK — ещё нет.
- **delivery** — `DeliveryOrder.document_id`.

Печатные формы MX-1 / MX-3 / ТОРГ-2 — этап 8, не этот модуль как «генератор PDF в роуте».
