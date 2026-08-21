# План: Консолидация entity-list и entity-system

## Цель
Полностью удалить `features/entity-list/` и перевести все страницы на `features/entity-system/`.

## Стратегия
Единовременная полная миграция без промежуточных этапов и заглушек.

## Шаги

### 1. Проверить полноту `entity-system`
Убедиться что `entity-system` имеет все возможности `entity-list`:
- [x] Базовый список
- [x] Фильтрация (текст, дата, select)
- [x] Сортировка
- [x] Выбор строк
- [x] Контекстное меню
- [x] Настройка колонок (порядок, видимость, ширина)
- [x] Экспорт CSV
- [x] Ссылки в ячейках
- [x] Кастомный рендер ячеек
- [x] Групповые действия
- [x] Действия со строкой
- [x] Вкладки на детальной странице
- [x] Секции на детальной странице
- [x] Формы редактирования

### 2. Обновить `entity-system/types.ts`
- Убедиться что `ColumnConfig` включает все поля из `entity-list`
- Добавить недостающие поля: `sortable`, `filterable`, `width`
- Убедиться что `ListPageConfig` покрывает все сценарии
- Проверить `ToolbarConfig`

### 3. Обновить `entity-system/hooks/useEntityList.ts`
- Добавить недостающие утилиты из `entity-list/columnUtils.ts`
- Убедиться что `formatCellValue`, `compareValues`, `filterValue` работают корректно
- Перенести `formatDt` если ещё не импортирован

### 4. Обновить все страницы
Заменить импорты:
- `../features/entity-list/EntityListPage` → `../features/entity-system/EntityListPage`
- `../features/entity-list/useEntityList` → `../features/entity-system/hooks/useEntityList`
- `../features/entity-list/types` → `../features/entity-system/types`

### 5. Обновить конфигурации сущностей
Все файлы в `features/*/config.ts`:
- Проверить типы на совместимость с новым `ListPageConfig`
- Добавить `toolbar` где отсутствует
- Убедиться что `columnOverrides` работают

### 6. Удалить `features/entity-list/`
Полностью удалить директорию:
- `EntityListPage.tsx`
- `useEntityList.ts`
- `columnUtils.ts`
- `types.ts`

### 7. Обновить детальные страницы
- Перевести на `EntityDetailPage` из `entity-system`
- Использовать секции и табы вместо ручного рендера
- Удалить ручные `DetailPageShell` если не нужен

### 8. Тестирование
- Проверить все страницы списков
- Проверить детальные страницы
- Проверить групповые действия
- Проверить экспорт CSV
- Проверить настройку колонок

## Файлы для изменений

### Страницы (замена импортов)
- AddressesPage.tsx
- AddressInputAliasesPage.tsx
- BatchesPage.tsx
- ClientsPage.tsx
- ContractsPage.tsx
- DeliveryOrdersPage.tsx
- DeliveryZonesPage.tsx
- DepositorsPage.tsx
- DocumentsPage.tsx
- DriversPage.tsx
- FilesPage.tsx
- IntegrationLogsPage.tsx
- IntegrationProfilesPage.tsx
- LegalEntitiesPage.tsx
- LpnsPage.tsx
- NotificationsPage.tsx
- ProductsPage.tsx
- RolesPage.tsx
- RoutesPage.tsx
- TariffsPage.tsx
- TasksPage.tsx
- TradePointsPage.tsx
- UsersPage.tsx
- VehiclesPage.tsx

### Конфигурации (проверка типов)
- features/addresses/config.ts
- features/addresses/addressInputAliasConfig.ts
- features/batches/config.ts
- features/clients/config.ts
- features/contracts/config.ts
- features/delivery-orders/config.ts
- features/delivery-zones/config.ts
- features/depositors/config.ts
- features/documents/config.ts
- features/drivers/config.ts
- features/files/config.ts
- features/integration-logs/config.ts
- features/integration-profiles/config.ts
- features/legal-entities/config.ts
- features/lpns/config.ts
- features/notifications/config.ts
- features/products/config.ts
- features/roles/config.ts
- features/routes/config.ts
- features/tariffs/config.ts
- features/tasks/config.ts
- features/trade-points/config.ts
- features/users/config.ts
- features/vehicles/config.ts

## Критерии готовности
- [ ] Все страницы используют `entity-system`
- [ ] Директория `entity-list` удалена
- [ ] Нет ошибок TypeScript
- [ ] Нет ошибок ESLint
- [ ] Все списки отображаются корректно
- [ ] Все фильтры работают
- [ ] Сортировка работает
- [ ] Выбор строк работает
- [ ] Экспорт CSV работает
- [ ] Настройка колонок работает
- [ ] Контекстное меню работает
- [ ] Групповые действия работают (где применимо)
- [ ] Детальные страницы работают
