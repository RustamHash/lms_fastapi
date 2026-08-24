# План: Правильные схемы API с вложенностями

## Цель
Все роуты возвращают правильные Pydantic-схемы с вложенными объектами.

## Принципы
1. Схема = ответ API
2. Вложенные объекты для связанных сущностей
3. model_validate вместо ручной сборки
4. selectinload для загрузки связей

## Какие роуты исправить

### Parties
- GET /depositors -> вложенный legal_entity
- GET /clients -> вложенные адреса
- GET /contracts -> вложенные customer, executor
- GET /legal-entities -> вложенные адреса
- GET /addresses -> вложенная delivery_zone

### Warehouse
- GET /products -> вложенная group
- GET /batches -> вложенный product
- GET /stock -> вложенные product, location
- GET /tasks/detail -> вложенные document, assignee, lines

### Orders
- GET /inbound-orders/{id}/detail -> вложенные depositor, supplier, lines
- GET /outbound-orders/{id}/detail -> вложенные depositor, client, lines

### Delivery
- GET /delivery/orders/detail -> вложенные outbound_order, route, driver
- GET /delivery/routes -> вложенные driver, vehicle

### Documents
- GET /documents/detail -> вложенные warehouse, lines

### Integration
- GET /integrations/profiles -> вложенный depositor

## Порядок работ
1. Parties (2-3 часа)
2. Warehouse (2-3 часа)
3. Orders (2 часа)
4. Delivery (1-2 часа)
5. Documents (1 час)
6. Integration (30 мин)

## Критерии приёмки
- Все роуты возвращают Pydantic-схемы
- Все связи через selectinload
- Нет N+1
- model_validate вместо ручной сборки
