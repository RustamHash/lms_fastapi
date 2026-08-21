# План фронтенд-реализации: Система фильтров и пресетов

## 1. Архитектура

### 1.1 Новые хуки

Файл: src/hooks/useTableSettings.ts

Назначение: Работа с настройками таблицы через API

Функции:
- Загрузка настроек: GET /api/v1/table-settings/{entityKey}
- Сохранение с debounce 500мс: PUT /api/v1/table-settings/{entityKey}
- Получение заводских: GET /api/v1/table-settings/{entityKey}/defaults
- Удаление настроек: DELETE /api/v1/table-settings/{entityKey}

Состояние:
- prefs: полный объект настроек
- isLoading: загрузка
- error: ошибка

Методы:
- save(prefs): сохранение с debounce
- resetToDefaults(): сброс к заводским
- clear(): удаление сохранённых

---

Файл: src/hooks/useListPresets.ts

Назначение: Работа с пресетами списков

Функции:
- Загрузка списка: GET /api/v1/list-presets/{entityKey}
- Создание: POST /api/v1/list-presets/{entityKey}
- Обновление: PUT /api/v1/list-presets/{entityKey}/{presetId}
- Удаление: DELETE /api/v1/list-presets/{entityKey}/{presetId}
- Применение: POST /api/v1/list-presets/{entityKey}/{presetId}/apply
- Установка по умолчанию: POST /api/v1/list-presets/{entityKey}/{presetId}/set-default

---

### 1.2 Модификация useEntityList

Файл: src/features/entity-system/hooks/useEntityList.tsx

Текущее состояние:
- filters: Record<string, string>
- excludeFilters: Record<string, string[]>
- sort: SortState
- prefs: useColumnPrefs

Новое состояние (добавляется):
- tableSettings: useTableSettings(entityKey)
- presets: useListPresets(entityKey)

Инициализация:
- filters из tableSettings.prefs.filters
- excludeFilters из tableSettings.prefs.exclude_filters
- sort из tableSettings.prefs.sort
- quickFilters из tableSettings.prefs.quick_filters

Автосохранение:
- useEffect с debounce 500мс
- Отслеживает: filters, excludeFilters, sort, quickFilters, order, hidden, widths
- Отправляет PUT при изменении

Методы:
- resetToDefaults(): сброс всех настроек к заводским
- applyPreset(presetId): применить пресет
- savePreset(name, config): сохранить пресет
- deletePreset(presetId): удалить пресет

---

## 2. UI компоненты

### 2.1 Панель активных фильтров

Файл: src/components/ActiveFiltersBar.tsx

Отображение:
- Чипы с активными фильтрами
- Каждый чип: название колонки + значение + крестик
- Кнопка "Сбросить все" если есть фильтры
- Кнопка "Сохранить пресет" если есть изменения
- Кнопка "Восстановить по умолчанию"

Расположение:
- Между тулбаром и таблицей
- Максимум 2 строки, дальше скролл
- Если фильтров нет — не показывается

---

### 2.2 Модальное окно настройки

Файл: src/components/ListSettingsDialog.tsx

Вкладки:
- Фильтры: все доступные фильтры с включением/выключением
- Колонки: видимость, порядок, ширина
- Сортировка: колонка и направление
- Пресеты: список, сохранение, применение

Кнопки:
- Применить
- Отмена
- Восстановить по умолчанию

---

### 2.3 Модальное окно сохранения пресета

Файл: src/components/SavePresetDialog.tsx

Поля:
- Название пресета (input)
- Чекбокс "Использовать по умолчанию"

Кнопки:
- Сохранить
- Отмена

---

## 3. Модификация EntityListPage

### 3.1 Добавление панели фильтров

Место: между тулбаром и таблицей

Условия показа:
- Если есть активные фильтры ИЛИ
- Если есть exclude_filters ИЛИ
- Если есть сохранённые пресеты

---

### 3.2 Добавление кнопок в тулбар

Новые кнопки:
- "Настроить" — открывает ListSettingsDialog
- "Пресеты" — выпадающий список пресетов
- "Сбросить" — сброс к заводским

---

## 4. Поток данных

### 4.1 Инициализация
1. useTableSettings загружает настройки с сервера
2. Если prefs есть — применяет
3. Если нет — использует дефолты из конфигурации

### 4.2 Изменение фильтра
1. Пользователь меняет фильтр
2. Обновляется локальное состояние
3. useEffect с debounce 500мс отправляет PUT
4. Сервер сохраняет

### 4.3 Применение пресета
1. Пользователь выбирает пресет
2. POST /apply
3. Сервер возвращает prefs
4. Локальное состояние обновляется
5. Таблица перерисовывается

### 4.4 Сохранение пресета
1. Пользователь настраивает фильтры/сортировку/колонки
2. Нажимает "Сохранить пресет"
3. Вводит название
4. POST /list-presets
5. Пресет появляется в списке

### 4.5 Сброс к заводским
1. GET /defaults
2. Полученные prefs применяются локально
3. DELETE /table-settings (удалить сохранённые)
4. Таблица обновляется

---

## 5. Типы TypeScript

### 5.1 TablePrefs
export type TablePrefs = {
  order: string[]
  hidden: string[]
  widths: Record<string, number>
  filters: Record<string, string>
  exclude_filters: Record<string, string[]>
  sort: { column: string | null; direction: 'asc' | 'desc' } | null
  quick_filters: string[]
}

### 5.2 ListPreset
export type ListPreset = {
  id: number
  name: string
  config: TablePrefs
  is_default: boolean
  created_at: string
  updated_at: string
}

---

## 6. Файлы для создания

Новые файлы:
- src/hooks/useTableSettings.ts
- src/hooks/useListPresets.ts
- src/components/ActiveFiltersBar.tsx
- src/components/ListSettingsDialog.tsx
- src/components/SavePresetDialog.tsx

Модифицируемые файлы:
- src/features/entity-system/hooks/useEntityList.tsx
- src/features/entity-system/EntityListPage.tsx
- src/components/ListTableShell.tsx

---

## 7. Порядок реализации

Этап 1: Базовые хуки
- useTableSettings
- useListPresets

Этап 2: Интеграция в useEntityList
- Инициализация из серверных настроек
- Автосохранение с debounce

Этап 3: UI панели фильтров
- ActiveFiltersBar
- Чипы фильтров
- Кнопки сброса

Этап 4: Модальное окно
- ListSettingsDialog
- Вкладки: фильтры, колонки, сортировка, пресеты

Этап 5: Пресеты
- SavePresetDialog
- Выпадающий список
- Применение и удаление

---

## 8. Тестирование

Проверить:
- Загрузка настроек при открытии
- Сохранение фильтров с debounce
- Сброс к заводским
- Создание пресета
- Применение пресета
- Удаление пресета
- Установка по умолчанию
- Сохранение сортировки
- Сохранение колонок
- Сохранение фильтров в шапке
