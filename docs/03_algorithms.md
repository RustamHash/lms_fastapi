# Бэкенд — алгоритмы

## 1. Создание адреса

AddressService.get_or_create:

1. Нормализация текста: " ".join(text.lower().strip().split())
2. Хеш SHA256 от нормализованного
3. Поиск в RawAddress по raw_text
4. Поиск в RawAddress по hash
5. DaData clean_address — получить нормализованный
6. Поиск в Address по fias_id
7. Поиск в Address по full_address
8. Создание Address + RawAddress

## 2. Приход товара

StockService.add_stock:

1. Найти StockBalance по (product, location, lpn, batch)
2. Если есть — увеличить quantity
3. Если нет — создать
4. Создать StockMovement (direction=in)

## 3. Расход товара

StockService.remove_stock:

1. Найти StockBalance
2. Проверить остаток
3. Уменьшить quantity
4. Создать StockMovement (direction=out)

## 4. Перемещение

StockService.move_stock:

1. remove_stock из from_location
2. add_stock в to_location

## 5. Резервирование

StockService.reserve:

1. Найти StockBalance
2. Проверить available = quantity - reserved_quantity
3. Увеличить reserved_quantity

## 6. FEFO размещение

PlacementService.find_location:

1. Получить закреплённые ячейки отбора (ProductLocation)
2. Для каждой проверить:
 - пустая → place
 - та же партия → place
 - другая партия, свежее → replace
 - другая партия, хуже → skip
3. Если ни одна не подошла — первая свободная ячейка хранения

## 7. Задания

TaskService.complete_line:

1. Автостарт задания (new → in_progress)
2. В зависимости от типа:
 - receiving/putaway → add_stock
 - picking/shipping → remove_stock
 - movement → move_stock
3. Накопить fact_qty
4. При завершении задания:
 - нет отклонений → completed
 - есть отклонения + force → completed_with_deviations

## 8. Импорт заказов

1. FTP: скачать файл
2. Adapter: парсинг XML → UniversalDoc
3. Для каждого товара: find or create Product
4. Создать Document
5. Для каждой строки: create DocumentLine
6. Если доставка: create DeliveryOrder

## 9. Аутентификация

1. POST /auth/token: username + password
2. Проверить bcrypt hash
3. Создать JWT (sub=user_id, exp=24h)
4. При каждом запросе: decode JWT, получить user
5. Проверить has_permission для действий
