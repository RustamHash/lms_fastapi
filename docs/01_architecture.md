# Общая архитектура

## Слои

HTTP Request → FastAPI Router (app/api/v1/) → Service (app//services/) → Repository (app//repository.py) → ORM Model (app/*/models/) → PostgreSQL

## Модули

| Модуль | Назначение |
|--------|------------|
| accounts | Пользователи, роли, аудит, настройки таблиц |
| parties | Адреса, юрлица, поклажедатели, клиенты, договоры, тарифы |
| warehouse | Топология склада, товары, партии, LPN, остатки, задания |
| documents | Документы прихода/расхода/перемещения |
| delivery | Доставка, водители, транспорт, маршруты |
| integration | FTP, адаптеры, импорт заказов |
| notifications | Уведомления |
| files | Загрузка/скачивание файлов |
| infrastructure | Базовые классы, UoW, аудит, логирование |
| core | Конфигурация, БД, безопасность, зависимости |

## Принципы

1. Router → Service → Repository → DB
2. Все запросы асинхронные
3. Soft delete через Base.soft_delete()
4. UoW управляет транзакциями
5. Валидация через Pydantic-схемы
