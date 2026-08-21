# План рефакторинга фронтенда LMS FastAPI

> Создан: $(date +%Y-%m-%d)
> Статус: черновик

---

## Цели

1. Удалить мёртвый код и неиспользуемые файлы
2. Устранить дублирование логики и констант
3. Декомпозировать крупные компоненты
4. Улучшить типизацию (убрать `any`)
5. Унифицировать API-клиент и обработку ошибок
6. Оптимизировать производительность (мемоизация)
7. Исправить CSS-проблемы

---

## Этап 1: Удаление мёртвого кода

### 1.1. Пустые файлы для удаления

- [ ] `src/features/entity-system/EntityTableShell.tsx`
- [ ] `src/features/entity-system/RowContextMenu.tsx`
- [ ] `src/features/entity-system/hooks/useEntityPrefs.ts`
- [ ] `src/features/addresses/tabs/DeliveryZoneTab.tsx`
- [ ] `src/features/addresses/tabs/AliasesTab.tsx`
- [ ] `src/features/addresses/components/AddressSearch.tsx`

### 1.2. Неиспользуемые компоненты

- [ ] Удалить `src/hooks/useListController.ts` (заменён на `useEntityList`)
- [ ] Удалить `TopologyBackBar` из `DetailPageShell` (или вынести как опцию)
- [ ] Удалить неиспользуемые `viewDialog*` пропсы из `ListTableShell`

### 1.3. Неиспользуемые зависимости

- [ ] Проверить `npm ls` на неиспользуемые пакеты
- [ ] Удалить `react-refresh` если не используется

---

## Этап 2: Устранение дублирования

### 2.1. Утилиты

- [ ] Объединить `formatDt` из `lib/formatDt.ts` и локальную копию в `useEntityList.tsx`
- [ ] Объединить словари `DOCUMENT_TYPES`, `DOCUMENT_STATUSES`, `TASK_TYPES` из `GenericDetailPage.tsx` и `lib/statusLabels.ts`

### 2.2. Конфиги

- [ ] Создать единый `types.ts` для всех конфигов сущностей
- [ ] Вынести общие фильтры (status, date) в переиспользуемые константы

### 2.3. CSS

- [ ] Убрать дублирующиеся импорты `variables.css` (сейчас в `index.css` и `App.css`)
- [ ] Удалить дублирующиеся правила `.task-filter__select:focus` (4 раза)
- [ ] Исправить незакрытый селектор `.topology-hub__card:hover`

---

## Этап 3: Декомпозиция крупных компонентов

### 3.1. `ListTableShell.tsx` (~700 строк)

- [ ] Вынести `TableToolbar` (кнопки обновить/создать/экспорт/вид/сброс)
- [ ] Вынести `TableHeader` (заголовки колонок, сортировка)
- [ ] Вынести `TableFilterRow` (строка фильтров)
- [ ] Вынести `TableBody` (строки данных, чекбоксы, контекстное меню)
- [ ] Вынести `ColumnPickerDialog` (диалог настройки колонок)
- [ ] Вынести `ResizeHandle` (drag для изменения ширины колонок)

### 3.2. `EntityListPage.tsx` (~300 строк)

- [ ] Создать хук `useColumnFilterConfigs` для конвертации колонок в фильтры
- [ ] Создать хук `useEntityActions` для обработки row/group actions
- [ ] Вынести логику экспорта CSV в `lib/exportCsv.ts`

### 3.3. `ImportDialog.tsx` (~250 строк)

- [ ] Вынести `useImportPolling` хук (long-polling логика)
- [ ] Вынести `ImportProgress` компонент (статистика, прогресс-бар)
- [ ] Вынести `ImportLog` компонент (лог сообщений)

---

## Этап 4: Улучшение типизации

### 4.1. Убрать `any`

- [ ] `EntityListPage.tsx`: заменить `Record<string, any>` на `Record<string, ColumnFilterDef>`
- [ ] `useEntityList.tsx`: типизировать возвращаемое значение `filterValue`
- [ ] `ListSettingsDialog.tsx`: типизировать `columnLabels` как `Record<string, string>`

### 4.2. Согласовать типы

- [ ] `FilterType` в `types.ts` должен включать `'bool'`
- [ ] `ColumnFilterDef` в `ListTableShell.tsx` должен использовать общий тип из `types.ts`
- [ ] `TablePrefs` должен иметь единый источник (сейчас дублируется в нескольких местах)

### 4.3. Generic-типы

- [ ] Создать `EntityListPageProps<Row>` с правильными generic
- [ ] Типизировать `useEntityList` возвращаемое значение
- [ ] Типизировать `GroupActionsBar` для конкретных сущностей

---

## Этап 5: Унификация API-клиента

### 5.1. Создать `ApiClient` класс

- [ ] Создать `src/lib/apiClient.ts` с методами:
  - `get<T>(url)` — GET запрос с типизацией
  - `post<T>(url, body)` — POST запрос
  - `put<T>(url, body)` — PUT запрос
  - `patch<T>(url, body)` — PATCH запрос
  - `delete(url)` — DELETE запрос
  - `upload(url, file)` — загрузка файла
  - `download(url)` — скачивание файла

### 5.2. Обработка ошибок

- [ ] Создать `ApiError` класс с полями `status`, `detail`
- [ ] Автоматически парсить `detail` из JSON
- [ ] Автоматически очищать токен при 401

### 5.3. AbortController

- [ ] Добавить поддержку `signal` в `apiFetch`
- [ ] Использовать `AbortController` во всех `useEffect` с запросами
- [ ] Создать хук `useAbortController` для автоматической отмены

---

## Этап 6: Оптимизация производительности

### 6.1. Мемоизация

- [ ] Мемоизировать `columnFilters` в `EntityListPage.tsx`
- [ ] Мемоизировать `filterValue` в `useEntityList.tsx`
- [ ] Мемоизировать `MENU_GROUPS` в `Navbar.tsx`
- [ ] Мемоизировать `TASK_TYPES` в `TasksPage.tsx`
- [ ] Мемоизировать `DT_MODES` в `ListFilterCell.tsx`

### 6.2. Виртуализация (отложено)

- [ ] НЕ внедрять сейчас — отложить до появления пагинации

### 6.3. React Query оптимизации

- [ ] Настроить `refetchOnWindowFocus: false` глобально
- [ ] Настроить `retry` для разных типов запросов
- [ ] Добавить `placeholderData` для плавной загрузки

---

## Этап 7: Исправление CSS

### 7.1. Структура

- [ ] Создать единый `styles/index.css` с импортами всех компонентов
- [ ] Удалить дублирующиеся импорты в `index.css` и `App.css`
- [ ] Разделить `App.css` на логические части

### 7.2. Синтаксические ошибки

- [ ] Исправить `.topology-hub__card:hover` (незакрытый селектор)
- [ ] Исправить `.task-filter__select:focus` (дублируется 4 раза)
- [ ] Проверить все CSS файлы линтером

### 7.3. Переменные

- [ ] Заменить «магические» цвета на переменные из `variables.css`
- [ ] Добавить недостающие переменные (spacing, breakpoints)

---

## Этап 8: Обработка ошибок

### 8.1. Граничные случаи

- [ ] Добавить проверку `res.ok` в `ContractCreatePage.tsx`
- [ ] Добавить проверку `res.ok` в `DepositorCreatePage.tsx`
- [ ] Обработать `null` в `AddressDetailPage.tsx`
- [ ] Обработать пустые списки в `ClientCreatePage.tsx`

### 8.2. Пользовательские сообщения

- [ ] Создать `src/lib/errorMessages.ts` с маппингом ошибок
- [ ] Использовать единый формат сообщений об ошибках
- [ ] Добавить toast-уведомления для асинхронных ошибок

---

## Этап 9: Безопасность

### 9.1. Токен

- [ ] Рассмотреть переход на `HttpOnly` cookie (обсудить с backend)
- [ ] Добавить CSRF-защиту для cookie-авторизации
- [ ] Добавить автоматический logout при истечении токена

### 9.2. Валидация

- [ ] Добавить валидацию форм (react-hook-form или zod)
- [ ] Валидировать `external_id` в `ClientCreatePage`
- [ ] Валидировать `inn`, `kpp`, `ogrn` в `LegalEntityCreatePage`

---

## Этап 10: Тестирование

### 10.1. Unit-тесты

- [ ] Настроить Vitest
- [ ] Тесты для `formatDt.ts`
- [ ] Тесты для `statusLabels.ts`
- [ ] Тесты для `filterEngine.ts`
- [ ] Тесты для `arrayMove.ts`

### 10.2. Компонентные тесты

- [ ] Тесты для `ListFilterCell.tsx`
- [ ] Тесты для `GenericDetailPage.tsx`
- [ ] Тесты для `DetailPageShell.tsx`

### 10.3. E2E-тесты

- [ ] Настроить Playwright
- [ ] Тест авторизации
- [ ] Тест навигации по справочникам
- [ ] Тест списка заказов

---

## Порядок выполнения

1. **Этап 1** — удаление мёртвого кода (1-2 часа)
2. **Этап 2** — устранение дублирования (2-3 часа)
3. **Этап 7** — исправление CSS (1 час)
4. **Этап 4** — улучшение типизации (3-4 часа)
5. **Этап 5** — унификация API-клиента (2-3 часа)
6. **Этап 3** — декомпозиция компонентов (4-6 часов)
7. **Этап 8** — обработка ошибок (2-3 часа)
8. **Этап 6** — оптимизация производительности (2-3 часа)
9. **Этап 9** — безопасность (2-3 часа)
10. **Этап 10** — тестирование (4-6 часов)

**Итого: примерно 25-35 часов**

---

## Критерии готовности

- [ ] Все пустые файлы удалены
- [ ] `npm run lint` проходит без ошибок
- [ ] `npm run build` проходит без ошибок
- [ ] `npx tsc --noEmit` не выдаёт предупреждений
- [ ] Нет дублирующихся констант
- [ ] Все компоненты типизированы
- [ ] API-клиент унифицирован
- [ ] Производительность не ухудшилась
- [ ] Все тесты проходят
