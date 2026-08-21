# ДЕТАЛЬНЫЙ ПЛАН: Производительность

## 📍 Текущая проблема

### 4.1 N+1 запросы в list_depositors
**Файл:** app/api/v1/parties/routes.py

Для каждого депозитора выполняется отдельный запрос к LegalEntity.

**Влияние:** 100 депозиторов = 101 запрос к БД.

### 4.2 N+1 запросы в list_aliases
**Файл:** app/api/v1/parties/routes.py

Для каждого RawAddress выполняется отдельный запрос к Address.

**Влияние:** 1000 алиасов = 1001 запрос к БД.

### 4.3 Отсутствие индексов на FK
**Файл:** Все модели

Нет индексов на ForeignKey колонках.

**Влияние:** Медленные JOIN запросы при росте данных.

### 4.4 Нет пагинации
**Файл:** Все роуты

Большинство списков возвращают все записи без limit/offset.

**Влияние:** Большие ответы, нагрузка на БД.

### 4.5 Нет фильтрации
**Файл:** Все роуты

Только фильтрация по ID, нет по датам, статусам, тексту.

**Влияние:** Невозможность эффективного поиска.

## 💡 Варианты решения

### Вариант A: Быстрые фиксы
Только N+1 запросы (4.1, 4.2)
- **Плюсы:** Быстро (3 часа)
- **Минусы:** Остаются проблемы масштабирования
- **Сложность:** Низкая
- **Влияние:** Среднее

### Вариант B: Комплексная оптимизация
N+1 + индексы + пагинация + фильтрация
- **Плюсы:** Полное решение
- **Минусы:** Много изменений (1-2 дня)
- **Сложность:** Высокая
- **Влияние:** Высокое

### Вариант C: Поэтапное улучшение
N+1 + индексы сначала, пагинация и фильтрация потом
- **Плюсы:** Управляемый риск
- **Минусы:** Дольше до полного решения
- **Сложность:** Средняя
- **Влияние:** Высокое

## 🔧 Рекомендуемое решение

**Вариант C** — сначала N+1 и индексы, затем пагинация.

## 📝 Шаги реализации

### N+1 запросы
1. [ ] В list_depositors использовать selectinload(Depositor.legal_entity)
2. [ ] В list_aliases использовать join для Address

### Индексы
3. [ ] Добавить index=True на все FK колонки:
   - [ ] Product.depositor_id
   - [ ] Product.external_id
   - [ ] StockBalance.product_id
   - [ ] StockBalance.location_id
   - [ ] StockMovement.product_id
   - [ ] Document.warehouse_id
   - [ ] DeliveryOrder.trade_point_id
   - [ ] Client.depositor_id

### Пагинация
4. [ ] Создать общую схему PaginationParams:
   - limit: int = Query(50, ge=1, le=500)
   - offset: int = Query(0, ge=0)
5. [ ] Применить ко всем list-роутам

### Фильтрация
6. [ ] Добавить query-параметры:
   - status, date_from, date_to, search
   - product_id, depositor_id, warehouse_id

## 🧪 Как проверить

Проверить количество запросов (должно быть 2 вместо 101):
python -c "
import asyncio
from sqlalchemy import event
from app.core.database import engine

@event.listens_for(engine.sync_engine, 'before_cursor_execute')
def count_queries(*args, **kwargs):
    print('SQL:', kwargs.get('statement', '')[:100])
"

Проверить индексы:
python -c "
from app.infrastructure.orm_base import Base
for table in Base.metadata.tables.values():
    for index in table.indexes:
        print(f'{table.name}.{index.name}')
"

Проверить пагинацию:
curl "http://localhost:8000/api/v1/products?limit=10&offset=0"

## 📚 Связанные файлы

- app/api/v1/parties/routes.py
- app/warehouse/models/product.py
- app/warehouse/models/stock_balance.py
- app/documents/models/document.py
- app/delivery/models/delivery_order.py

## ⚠️ Риски

- Индексы замедляют INSERT/UPDATE
- Пагинация может сломать фронтенд если он ожидает все записи
- Фильтрация требует согласования с фронтендом
