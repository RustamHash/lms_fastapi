# Полный план рефакторинга и развития фронтенда LMS FastAPI

> Создан: 2026-08-22
> Обновлён: 2026-08-22
> Статус: актуальный

---

## 1. Выполненные работы

### 1.1. Рефакторинг (завершено)

- [x] Удалён мёртвый код (7 файлов)
- [x] Миграция apiFetch -> apiClient (26 файлов)
- [x] Декомпозиция ListTableShell (700 -> 397 строк + 5 файлов)
- [x] Декомпозиция EntityListPage (400 -> 336 строк + 3 файла)
- [x] Исправлены все .ok / .json() паттерны
- [x] Исправлены URL адресов (/list, /detail)
- [x] Исправлена зона доставки (zone_name в списке, delivery_zone.name в деталях)

### 1.2. Проверки

- [x] TypeScript: 0 ошибок
- [x] ESLint: 0 ошибок, 0 предупреждений
- [x] Сборка: успешно

---

## 2. Известные проблемы

### 2.1. Разрозненность hub-страниц

| Файл | Проблема | Статус |
|------|----------|--------|
| ReferencesPage.tsx | Карточки ref-card, без иконок | Требует обновления |
| OrdersHubPage.tsx | Минимальный | Требует обновления |
| DocumentsHubPage.tsx | Дублирует ссылки | Требует обновления |
| FilesHubPage.tsx | Заглушка | Требует обновления |
| TopologyHubPage | Не существует | Создать |
| ReportsHubPage | Не существует | Создать |
| SystemHubPage | Не существует | Создать |
| IntegrationsHubPage | Не существует | Создать |

### 2.2. Проблемы в хуках

**useColumnPrefs.ts:**
- [ ] Новые колонки не добавляются автоматически при обновлении конфига
- [ ] Лишние зависимости в useCallback

**useEntityList.tsx:**
- [ ] filterValue дублирует логику filterEngine.ts
- [ ] formatCellValue дублирует formatDt
- [ ] columnFilters использует Record<string, any>

**useListPresets.ts:**
- [ ] applyPreset возвращает результат, который игнорируется
- [ ] setDefaultPreset обновляет только локально

**useTableSettings.ts:**
- [ ] Debounce 500мс может быть долгим
- [ ] save() не возвращает Promise

### 2.3. Обработка ошибок

- [ ] Нет ErrorBoundary
- [ ] 401 не обрабатывается централизованно
- [ ] Нет страницы 404

### 2.4. Типизация

- [ ] EntityListPage.tsx: Record<string, any> (2 места)
- [ ] types.ts: format: (value: any)
- [ ] ImportDialog.tsx: documentTypeRef.current не типизирован
- [ ] AddressDetailPage.tsx: data тип unknown

### 2.5. Производительность

- [ ] Нет пагинации (все списки грузятся целиком)
- [ ] Нет виртуализации (1000+ строк)
- [ ] filterValueFromRow пересоздаётся каждый рендер
- [ ] columnFilters не мемоизирован

### 2.6. CSS

- [ ] Дублирование .task-filter__select:focus (3 раза)
- [ ] Мёртвые стили .app-ref-menu, .app-submenu
- [ ] Нет стилей для HubPage, ReportBuilder
- [ ] variables.css импортируется 2 раза

---

## 3. Hub-страницы

### 3.1. Создать компонент HubPage

**Файл:** src/components/HubPage.tsx
**CSS:** src/styles/components/hub.css

Функциональность:
- [ ] Секции с группами ссылок
- [ ] Иконки, описания, счётчики
- [ ] Адаптивная сетка
- [ ] Breadcrumbs
- [ ] Actions в шапке

### 3.2. Обновить существующие

- [ ] ReferencesPage -> HubPage
- [ ] OrdersHubPage -> HubPage
- [ ] DocumentsHubPage -> HubPage
- [ ] FilesHubPage -> HubPage

### 3.3. Создать новые

- [ ] DeliveryHubPage
- [ ] SystemHubPage
- [ ] IntegrationsHubPage
- [ ] TopologyHubPage
- [ ] ReportsHubPage

### 3.4. Обновить Navbar

- [ ] Добавить Топология
- [ ] Добавить Отчёты (отдельный пункт)

---

## 4. Подсистема отчётов

### 4.1. Типы

**Файл:** src/features/reports/types.ts

- [ ] ReportField
- [ ] ReportFilter
- [ ] ReportGrouping
- [ ] ReportConfig
- [ ] ReportResult
- [ ] ReportPreset

### 4.2. Метаданные полей

**Файл:** src/features/reports/stockReportConfig.ts
- [ ] Stock: quantity, reserved_quantity
- [ ] Product: name, sku, external_id
- [ ] Warehouse: name
- [ ] Location: name, location_type
- [ ] Zone: name, zone_type
- [ ] Depositor: code, name
- [ ] LPN: number, status
- [ ] Batch: batch_number, dates

**Файл:** src/features/reports/movementsReportConfig.ts
- [ ] Movement: id, quantity, type, date
- [ ] Product: name, sku
- [ ] FromLocation/ToLocation
- [ ] Document: number, type

### 4.3. ReportBuilder

**Файл:** src/features/reports/ReportBuilder.tsx

Табы:
- [ ] Период (from/to)
- [ ] Фильтры (поле + оператор + значение)
- [ ] Группировки (чекбоксы, drag-and-drop, итоги)
- [ ] Поля (дерево Модель->Поля, drag-and-drop)

Кнопки:
- [ ] Сформировать (только после настройки)
- [ ] Сохранить настройку
- [ ] Сбросить

### 4.4. Страницы отчётов

- [ ] StockReportPage
- [ ] MovementsReportPage
- [ ] Экспорт CSV
- [ ] Сохранение пресетов

### 4.5. Backend API

- [ ] POST /api/v1/reports/stock
- [ ] POST /api/v1/reports/movements
- [ ] GET/POST/PUT/DELETE /api/v1/reports/presets

---

## 5. Поддержка вложенных полей

### 5.1. Расширить ColumnConfig

- [ ] Добавить path (product.name)
- [ ] Создать getNestedValue

### 5.2. Обновить useEntityList

- [ ] Использовать path для отображения
- [ ] Сортировка по вложенным полям
- [ ] Фильтрация по вложенным полям

---

## 6. Приоритеты

| Приоритет | Задача | Оценка |
|-----------|--------|--------|
| P0 | ErrorBoundary | 30 мин |
| P0 | HubPage + обновление hub-страниц | 3-4 часа |
| P0 | Отчёты (типы + Builder + страницы) | 6-8 часов |
| P1 | Вложенные поля | 2-3 часа |
| P1 | Убрать any | 1 час |
| P2 | Пагинация | 4-6 часов |
| P2 | Виртуализация | 3-4 часа |
| P3 | CSS-очистка | 1-2 часа |

**Общий объём P0+P1: 12-16 часов**

---

## 7. Критерии готовности

- [ ] Все hub-страницы используют HubPage
- [ ] Отчёты формируются после настройки
- [ ] Вложенные поля отображаются
- [ ] Нет any в коде
- [ ] ErrorBoundary перехватывает ошибки
- [ ] Все проверки проходят
