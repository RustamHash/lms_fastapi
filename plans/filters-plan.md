# ТЗ для бэкенда: Система фильтров и пресетов списков

## 1. Общие требования

### 1.1 Цель
Реализовать серверное хранение настроек списков: фильтры, сортировка, конфигурация колонок, пресеты.

### 1.2 Принципы
- Все настройки привязаны к пользователю
- Синхронизация между устройствами через сервер
- Автосохранение при изменении
- Поддержка именованных пресетов
- Один пресет может быть назначен "по умолчанию"

---

## 2. Существующая система

### 2.1 Текущий эндпоинт
GET /api/v1/table-settings/{entityKey}
PUT /api/v1/table-settings/{entityKey}

### 2.2 Текущая модель данных
Таблица: ui_list_preferences

Поля:
- id: int, primary key
- user_id: int, foreign key -> users.id
- entity_key: varchar
- prefs: jsonb

### 2.3 Текущая структура prefs
{
  "order": ["id", "name", "inn"],
  "hidden": ["internal_id"],
  "widths": { "id": 80, "name": 200 }
}

---

## 3. Расширенная структура prefs

{
  "order": ["id", "name", "inn"],
  "hidden": ["internal_id"],
  "widths": { "id": 80, "name": 200 },
  "filters": {
    "name": "Иванов",
    "is_active": "true"
  },
  "exclude_filters": {
    "city": ["Москва", "Питер"]
  },
  "sort": {
    "column": "name",
    "direction": "asc"
  },
  "quick_filters": ["name", "is_active"],
  "active_preset_id": 123
}

Описание полей:
- order: массив id колонок в порядке отображения
- hidden: массив id скрытых колонок
- widths: объект id колонки -> ширина в px (4-480)
- filters: объект id колонки -> строковое значение фильтра
- exclude_filters: объект id колонки -> массив исключаемых значений
- sort: объект с column (id колонки или null) и direction (asc или desc)
- quick_filters: массив id колонок, которые показываются в шапке
- active_preset_id: id активного пресета или null

---

## 4. Новая таблица ui_list_presets

CREATE TABLE ui_list_presets (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    entity_key VARCHAR(255) NOT NULL,
    name VARCHAR(255) NOT NULL,
    config JSONB NOT NULL DEFAULT '{}'::jsonb,
    is_default BOOLEAN NOT NULL DEFAULT false,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE (user_id, entity_key, name)
);

CREATE INDEX idx_ui_list_presets_user_entity 
    ON ui_list_presets(user_id, entity_key);

Поле config имеет ту же структуру, что и prefs.

---

## 5. API эндпоинты

### 5.1 Настройки списка (расширенные)

GET /api/v1/table-settings/{entityKey}
- Получить настройки для текущего пользователя
- Если нет сохранённых — вернуть дефолтные
- Ответ: { "prefs": { ... } }

PUT /api/v1/table-settings/{entityKey}
- Сохранить настройки
- Тело: { "prefs": { ... } }
- Ответ: { "prefs": { ... } } (сохранённые)

---

### 5.2 Пресеты

GET /api/v1/list-presets/{entityKey}
- Получить список пресетов пользователя
- Ответ: { "presets": [ { id, name, config, is_default, created_at, updated_at } ] }

POST /api/v1/list-presets/{entityKey}
- Создать пресет
- Тело: { "name": "...", "config": { ... }, "is_default": false }
- Ответ: созданный пресет

PUT /api/v1/list-presets/{entityKey}/{presetId}
- Обновить пресет
- Тело: { "name": "...", "config": { ... } }

DELETE /api/v1/list-presets/{entityKey}/{presetId}
- Удалить пресет

POST /api/v1/list-presets/{entityKey}/{presetId}/apply
- Применить пресет
- Сохраняет config как текущие настройки в table-settings
- Ответ: { "prefs": { ... } }

POST /api/v1/list-presets/{entityKey}/{presetId}/set-default
- Установить пресет как "по умолчанию"
- Снимает is_default у других пресетов этой сущности
- Ответ: обновлённый пресет

---

## 6. Валидация

Общие правила:
- entityKey: строка, [a-zA-Z0-9_-]+, до 255 символов
- name: не пустая, до 255 символов
- config: содержит обязательные поля order, hidden, widths, filters, exclude_filters, sort, quick_filters

Специфические проверки:
- sort.direction: только 'asc' или 'desc'
- widths: числа от 4 до 480
- quick_filters: подмножество order
- filters: ключи — строки до 100 символов, значения — строки
- exclude_filters: значения — массивы строк

---

## 7. Обработка ошибок

Коды:
- 200: успех
- 400: невалидные данные
- 401: не авторизован
- 404: пресет не найден
- 409: дубликат названия пресета
- 422: ошибка валидации

Формат ошибки:
{
  "detail": "Человекочитаемое сообщение"
}

---

## 8. Права доступа

- Пользователь работает только со своими настройками и пресетами
- Нельзя получить чужие настройки или пресеты
- Администратор может видеть все (опционально)

---

## 9. Производительность

- Все запросы — точечные (по user_id + entity_key)
- Индекс на (user_id, entity_key) для ui_list_preferences
- Индекс на (user_id, entity_key) для ui_list_presets
- Кэширование на клиенте (staleTime 5 минут для настроек, 30 минут для пресетов)

---

## 10. Миграция данных

При расширении prefs:
- Существующие записи сохраняются
- Новые поля добавляются с дефолтными значениями:
  - filters: {}
  - exclude_filters: {}
  - sort: { column: null, direction: "asc" }
  - quick_filters: []
  - active_preset_id: null

