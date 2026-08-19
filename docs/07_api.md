# API — эндпоинты

## Auth

- POST /api/v1/auth/token — вход, получение JWT
- POST /api/v1/auth/register — регистрация
- GET /api/v1/auth/me — текущий пользователь + permissions

## Users

- GET /api/v1/users — список
- GET /api/v1/users/{id} — один
- PATCH /api/v1/users/{id} — обновить

## Roles

- GET /api/v1/roles — список
- POST /api/v1/roles — создать

## Table Settings

- GET /api/v1/table-settings/{table_id} — получить
- PUT /api/v1/table-settings/{table_id} — сохранить

## Parties — Addresses

- GET /api/v1/parties/addresses — список
- POST /api/v1/parties/addresses/resolve — создать/найти
- GET /api/v1/parties/addresses/{id} — один
- PATCH /api/v1/parties/addresses/{id} — обновить
- DELETE /api/v1/parties/addresses/{id} — удалить

## Parties — Aliases

- GET /api/v1/parties/aliases — список
- GET /api/v1/parties/aliases/{id} — один
- DELETE /api/v1/parties/aliases/{id} — удалить

## Parties — Legal Entities

- GET /api/v1/parties/legal-entities — список
- POST /api/v1/parties/legal-entities — создать
- GET /api/v1/parties/legal-entities/{id} — один
- PATCH /api/v1/parties/legal-entities/{id} — обновить
- DELETE /api/v1/parties/legal-entities/{id} — удалить

## Parties — Depositors

- GET /api/v1/parties/depositors — список
- POST /api/v1/parties/depositors — создать
- GET /api/v1/parties/depositors/{id} — один
- PATCH /api/v1/parties/depositors/{id} — обновить
- DELETE /api/v1/parties/depositors/{id} — удалить

## Parties — Clients

- GET /api/v1/parties/clients — список
- POST /api/v1/parties/clients — создать
- GET /api/v1/parties/clients/{id} — один
- PATCH /api/v1/parties/clients/{id} — обновить
- DELETE /api/v1/parties/clients/{id} — удалить

## Parties — Trade Points

- GET /api/v1/parties/trade-points — список
- POST /api/v1/parties/trade-points/resolve — создать/найти
- GET /api/v1/parties/trade-points/{id} — один
- PATCH /api/v1/parties/trade-points/{id} — обновить
- DELETE /api/v1/parties/trade-points/{id} — удалить

## Parties — Contracts

- GET /api/v1/parties/contracts — список
- POST /api/v1/parties/contracts — создать
- GET /api/v1/parties/contracts/{id} — один
- PATCH /api/v1/parties/contracts/{id} — обновить
- DELETE /api/v1/parties/contracts/{id} — удалить

## Parties — Tariffs

- GET /api/v1/parties/tariff-documents — список
- POST /api/v1/parties/tariff-documents — создать
- GET /api/v1/parties/tariff-documents/{id} — один
- PATCH /api/v1/parties/tariff-documents/{id} — обновить
- DELETE /api/v1/parties/tariff-documents/{id} — удалить
- GET /api/v1/parties/tariffs — список
- POST /api/v1/parties/tariffs — создать
- GET /api/v1/parties/tariffs/{id} — один
- PATCH /api/v1/parties/tariffs/{id} — обновить
- DELETE /api/v1/parties/tariffs/{id} — удалить

## Warehouse — Products

- GET /api/v1/warehouse/products — список
- POST /api/v1/warehouse/products — создать
- GET /api/v1/warehouse/products/{id} — один
- PATCH /api/v1/warehouse/products/{id} — обновить
- DELETE /api/v1/warehouse/products/{id} — удалить

## Warehouse — Batches

- GET /api/v1/warehouse/batches — список
- POST /api/v1/warehouse/batches — создать
- GET /api/v1/warehouse/batches/{id} — один
- DELETE /api/v1/warehouse/batches/{id} — удалить

## Warehouse — LPN

- GET /api/v1/warehouse/lpns — список
- POST /api/v1/warehouse/lpns — создать
- GET /api/v1/warehouse/lpns/{id} — один
- DELETE /api/v1/warehouse/lpns/{id} — удалить

## Warehouse — Stock

- POST /api/v1/warehouse/stock/add — приход
- POST /api/v1/warehouse/stock/remove — расход
- POST /api/v1/warehouse/stock/move — перемещение

## Warehouse — Tasks

- GET /api/v1/warehouse/tasks — список
- POST /api/v1/warehouse/tasks — создать
- GET /api/v1/warehouse/tasks/{id} — один
- DELETE /api/v1/warehouse/tasks/{id} — удалить
- POST /api/v1/warehouse/tasks/{id}/lines — добавить строку
- POST /api/v1/warehouse/tasks/{id}/start — начать
- POST /api/v1/warehouse/tasks/{id}/complete — завершить
- POST /api/v1/warehouse/task-lines/{id}/complete — выполнить строку

## Documents

- GET /api/v1/documents — список
- POST /api/v1/documents — создать
- GET /api/v1/documents/{id} — один
- DELETE /api/v1/documents/{id} — удалить
- POST /api/v1/documents/{id}/lines — добавить строку
- PATCH /api/v1/documents/{id}/status — сменить статус

## Delivery

- GET /api/v1/delivery/orders — список
- POST /api/v1/delivery/orders — создать
- GET /api/v1/delivery/orders/{id} — один
- PATCH /api/v1/delivery/orders/{id}/status — статус

## Notifications

- GET /api/v1/notifications — список
- GET /api/v1/notifications/unread — непрочитанные
- POST /api/v1/notifications — создать
- POST /api/v1/notifications/{id}/read — отметить прочитанным
- POST /api/v1/notifications/{id}/unread — отметить непрочитанным
