# ДЕТАЛЬНЫЙ ПЛАН: Архитектура и дублирование

## 📍 Текущая проблема

### 1.1 Дублирование files_router
**Файл:** app/api/v1/router.py (строки 19-20, 28-29)

Проблема:
- Импорт files_router выполняется дважды
- include_router вызывается дважды

**Влияние:** Дублирование endpoint в OpenAPI, возможные конфликты маршрутов.

### 1.2 Дублирование модуля files
**Файлы:**
- app/api/v1/files/routes.py — API endpoints (активные)
- app/api/v1/files/schemas.py — Pydantic схемы
- app/infrastructure/files/models.py — SQLAlchemy модель
- app/infrastructure/files/repository.py — ПУСТОЙ
- app/infrastructure/files/routes.py — ПУСТОЙ
- app/infrastructure/files/schemas.py — ПУСТОЙ
- app/infrastructure/files/service.py — ПУСТОЙ

**Влияние:** Путаница в структуре, сложность поддержки.

### 1.3 Дублирование Pydantic схем
**Файл:** app/api/v1/parties/schemas.py

Дублируются классы:
- LegalEntityUpdate (строки 190-205 и 291-306)
- ClientUpdate (строки 240-247 и 314-321)

**Влияние:** Неопределенность какая схема используется, баги при изменении.

### 1.4 Пустые файлы
- app/delivery/repository.py
- app/documents/repository.py
- app/integration/repository.py
- app/integration/ftp_service.py
- app/notifications/repository.py
- app/warehouse/repository.py
- app/warehouse/placement.py
- app/core/middleware.py
- app/infrastructure/audit/events.py
- app/infrastructure/audit/service.py

**Влияние:** Создают ложное впечатление о структуре.

## 💡 Варианты решения

### Вариант A: Минимальные изменения
Удалить только дубли, не трогая структуру
- **Плюсы:** Быстро, безопасно
- **Минусы:** Структура останется неоптимальной
- **Сложность:** 1 час
- **Влияние:** Низкое

### Вариант B: Реорганизация структуры
Полностью пересмотреть структуру модулей
- **Плюсы:** Чистая архитектура
- **Минусы:** Много изменений, риск сломать импорты
- **Сложность:** 2-3 дня
- **Влияние:** Высокое

### Вариант C: Компромиссный
Удалить дубли + консолидировать files в одно место
- **Плюсы:** Баланс чистоты и рисков
- **Минусы:** Нужно обновить импорты
- **Сложность:** 2-3 часа
- **Влияние:** Среднее

## 🔧 Рекомендуемое решение

**Вариант C** — удалить дубли, консолидировать files, удалить пустые файлы.

## 📝 Шаги реализации

1. [ ] В router.py удалить дублирование импорта и include_router
2. [ ] В parties/schemas.py удалить дубли LegalEntityUpdate (оставить первый)
3. [ ] В parties/schemas.py удалить дубли ClientUpdate (оставить первый)
4. [ ] Объединить files:
   - [ ] Перенести routes.py в app/infrastructure/files/routes.py
   - [ ] Перенести schemas.py в app/infrastructure/files/schemas.py
   - [ ] Обновить импорт в router.py
   - [ ] Удалить директорию app/api/v1/files/
5. [ ] Удалить все пустые файлы из списка 1.4
6. [ ] Обновить __init__.py файлы при необходимости

## 🧪 Как проверить

Проверить отсутствие дублей в OpenAPI:
curl http://localhost:8000/openapi.json | jq '.paths | keys[]' | sort | uniq -d

Проверить отсутствие пустых Python файлов:
find app -name "*.py" -empty

Проверить, что все импорты работают:
python -c "from app.api.v1.router import api_router; print('OK')"

Запустить приложение:
uvicorn app.main:app --reload

## 📚 Связанные файлы

- app/api/v1/router.py
- app/api/v1/parties/schemas.py
- app/api/v1/files/
- app/infrastructure/files/

## ⚠️ Риски

- Ошибки импорта: внимательно обновить все import пути
- Фронтенд: убедиться, что API endpoints не изменились (URL)
- Миграции: убедиться, что модель File осталась в app.infrastructure.files.models
