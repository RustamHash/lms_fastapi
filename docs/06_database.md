# База данных — модели

## Базовые поля (Base)

Все модели наследуют:

- id — integer, autoincrement
- is_active — boolean, default true
- created_at — datetime
- updated_at — datetime
- created_by_id — FK на accounts_user
- updated_by_id — FK на accounts_user
- is_deleted — boolean, soft delete
- deleted_at — datetime
- deleted_by_id — FK на accounts_user

## Методы Base

- activate(user_id) — включить
- deactivate(user_id) — выключить
- soft_delete(user_id) — удалить
- restore(user_id) — восстановить

## Связи

accounts_user → accounts_user_roles → accounts_role
accounts_user → accounts_user_depositor → parties_depositor
accounts_user → accounts_user_trade_point → parties_trade_point

parties_legal_entity → parties_depositor (OneToOne)
parties_legal_entity → parties_keeper (OneToOne)
parties_legal_entity → parties_carrier (OneToOne)
parties_depositor → parties_client → parties_trade_point
parties_legal_entity → parties_contract → parties_tariff_document → parties_tariff

parties_address → parties_raw_address
parties_address → parties_trade_point
parties_delivery_zone → parties_address

warehouse_warehouse → warehouse_virtual_warehouse
warehouse_warehouse → warehouse_zone → warehouse_row → warehouse_location
warehouse_product → warehouse_package
warehouse_product → warehouse_batch
warehouse_product → warehouse_stock_balance
warehouse_product → warehouse_stock_movement
warehouse_product → warehouse_task_line

documents_document → documents_document_line
documents_document → warehouse_task
documents_document_line → warehouse_task_line

delivery_order → delivery_route_line
delivery_route → delivery_route_line
delivery_driver → delivery_route
delivery_vehicle → delivery_route
