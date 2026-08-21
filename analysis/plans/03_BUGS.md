# ДЕТАЛЬНЫЙ ПЛАН: Баги и ошибки

## 📍 Текущая проблема

### 3.1 LPN.number не генерируется
**Файл:** app/warehouse/models/lpn.py + app/warehouse/services/lpn_service.py

number имеет unique=True и NOT NULL, но в LPNService.create() не устанавливается.

**Влияние:** Ошибка NOT NULL constraint при создании LPN.

### 3.2 SQL NULL-проверки
**Файл:** app/warehouse/services/stock_service.py

В get_balance() используется lpn_id == None и batch_id == None, что генерирует SQL "= NULL" вместо "IS NULL".

**Влияние:** Поиск с NULL параметрами не находит записи.

### 3.3 Даты в Notification как String
**Файл:** app/notifications/models/notification.py

sent_at и read_at имеют тип String(50) вместо DateTime.

**Влияние:** Нет сортировки по дате, нет временных зон.

### 3.4 Дублирование логов
**Файл:** app/warehouse/services/stock_service.py (строки 117-118)

В add_stock() выводится "Приход" и "Расход" одновременно.

**Влияние:** Неправильная диагностика.

### 3.5 User.roles relationship
**Файл:** app/accounts/models/user.py

secondary="accounts_user_roles" строкой вместо переменной user_roles.

**Влияние:** Может сломаться при переименовании таблицы.

## 💡 Варианты решения

### Вариант A: Быстрые фиксы
Исправить только критические баги (3.1, 3.2, 3.4)
- **Плюсы:** Быстро (2 часа)
- **Минусы:** Остаются скрытые проблемы
- **Сложность:** Низкая
- **Влияние:** Высокое

### Вариант B: Полное исправление
Исправить все баги + добавить тесты
- **Плюсы:** Надежность
- **Минусы:** Больше времени (полдня)
- **Сложность:** Средняя
- **Влияние:** Высокое

## 🔧 Рекомендуемое решение

**Вариант B** — все баги + тесты.

## 📝 Шаги реализации

### 3.1 LPN.number
1. [ ] В LPNService.create() добавить генерацию:
number = "LPN" + uuid.uuid4().hex[:12].upper()

### 3.2 SQL NULL
2. [ ] В get_balance() использовать .is_(None) для lpn_id и batch_id

### 3.3 DateTime в Notification
3. [ ] Изменить модель: sent_at и read_at на DateTime(timezone=True)
4. [ ] Обновить сервис: datetime.now(timezone.utc)
5. [ ] Создать миграцию Alembic

### 3.4 Дублирование логов
6. [ ] В add_stock() убрать строку "Расход"

### 3.5 User.roles relationship
7. [ ] Импортировать user_roles из role.py и использовать secondary=user_roles

## 🧪 Как проверить

Создать LPN:
curl -X POST http://localhost:8000/api/v1/warehouse/lpns -H "Authorization: Bearer TOKEN" -H "Content-Type: application/json" -d '{"status":"created"}'

Проверить SQL NULL (должен найти записи):
python -c "from app.warehouse.services.stock_service import StockService; print('OK')"

Проверить типы дат:
python -c "from app.notifications.models import Notification; print(Notification.__table__.columns['sent_at'].type)"

## 📚 Связанные файлы

- app/warehouse/models/lpn.py
- app/warehouse/services/lpn_service.py
- app/warehouse/services/stock_service.py
- app/notifications/models/notification.py
- app/notifications/services/notification_service.py
- app/accounts/models/user.py
- app/accounts/models/role.py

## ⚠️ Риски

- Миграция DateTime может потребовать конвертации существующих данных
- Изменение relationship может затронуть загрузку ролей
