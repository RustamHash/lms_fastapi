# Полный план рефакторинга: Качество, Производительность, Архитектура

## Цель
Исправить критические проблемы, устранить риски, оптимизировать узкие места и улучшить архитектуру.

## Приоритеты
- **P0** — Критические (падают запросы, теряются данные, дыры в безопасности)
- **P1** — Важные (N+1, ошибки без обработки, нарушение архитектуры)
- **P2** — Оптимизации (скорость, память, дополнительные улучшения)

---

# ЧАСТЬ 1: P0 — КРИТИЧЕСКИЕ ИСПРАВЛЕНИЯ

## 1. Обработка ошибок в session.flush() / session.commit()

**Проблема:** Ошибка БД оставляет транзакцию в неопределённом состоянии.

**Файлы:** все роуты и сервисы

**Решение:** Обернуть все session.flush() в try/except, при ошибке — rollback + логирование + HTTP 500.

**Оценка:** 2-3 часа

---

## 2. Pydantic-валидация вместо body: dict

**Файлы:**
- accounts/routes_user_settings.py — 4 роута
- warehouse/routes_references.py — 10+ роутов
- warehouse/routes.py — 2 роута
- delivery/routes_deviations_lines.py — 2 роута
- notifications/routes_rules.py — 1 роут

**Оценка:** 2 часа

---

## 3. Безопасность: защита файлов

**Файлы:** files/routes.py

**Проблемы:** Path traversal, нет проверки типа, нет ограничения размера.

**Решение:** Проверка расширений, размера, нормализация пути.

**Оценка:** 30 мин

---

## 4. Безопасность: JWT secret fallback

**Файл:** core/config.py

**Решение:** Генерировать случайный ключ при старте, если не задан.

**Оценка:** 5 мин

---

## 5. Безопасность: Rate limiting

**Файл:** core/middleware.py

**Решение:** Rate limiting для /auth/token и /auth/register.

**Оценка:** 1 час

---

# ЧАСТЬ 2: P1 — ВАЖНЫЕ ИСПРАВЛЕНИЯ

## 6. N+1 запросы — selectinload во все list-роуты

| Файл | Роут | Связи |
|------|------|-------|
| parties/routes.py | list_depositors | Depositor.legal_entity |
| orders/routes_inbound.py | list_inbound_orders_for_table | depositor, supplier, warehouse |
| orders/routes_outbound.py | list_outbound_orders_for_table | depositor, client, warehouse |
| delivery/routes.py | list_delivery_orders_for_table | outbound_order, route, driver, vehicle |
| documents/routes.py | list_documents_for_table | warehouse |
| warehouse/routes.py | list_tasks_for_table | document, assignee |

**Оценка:** 1-2 часа

---

## 7. Объединить запросы _get_order_*

**Файл:** orders/routes_outbound.py

**Оценка:** 30 мин

---

## 8. Синхронные операции — async

| Файл | Замена |
|------|--------|
| files/routes.py | aiofiles |
| integration/ftp_service.py | aioftp |
| notifications/email_adapter.py | aiofiles |

**Оценка:** 3-4 часа

---

## 9. Логирование в except-блоках

**Файлы:** routes_import.py, integration_service.py, middleware.py

**Оценка:** 30 мин

---

## 10. Каскадное удаление

**Модели:** Document-DocumentLine, Task-TaskLine, Route-RouteLine

**Оценка:** 30 мин

---

## 11. Конкурентность — SELECT FOR UPDATE

**Файлы:** stock_service.py, task_service.py

**Оценка:** 1 час

---

## 12. Утечки ресурсов

**Файлы:** routes_import.py (FTP), database.py

**Оценка:** 1 час

---

# ЧАСТЬ 3: P2 — АРХИТЕКТУРНЫЕ УЛУЧШЕНИЯ

## 13. Вынести бизнес-логику из роутов в сервисы

**Файлы:** все routes*.py

**Оценка:** 3-4 часа

---

## 14. BaseRepository

**Решение:** Единый базовый класс для всех репозиториев.

**Оценка:** 1 час

---

## 15. Стандартизировать сигнатуры сервисов

**Оценка:** 1-2 часа

---

## 16. Dependency Injection через Depends()

**Оценка:** 2-3 часа

---

## 17. Разделить integration_service

**Решение:** ProductImportService, OrderImportService, DocumentImportService.

**Оценка:** 2 часа

---

## 18. Убрать бизнес-логику из моделей

**Файлы:** accounts/models/user.py, infrastructure/orm_base.py

**Оценка:** 1-2 часа

---

## 19. Единый формат ответов API

**Оценка:** 1 час

---

# ЧАСТЬ 4: P2 — ОПТИМИЗАЦИИ

## 20. get_available_quantity — SQL вместо Python

**Файл:** warehouse/services/stock_service.py

**Оценка:** 30 мин

---

## 21. AddressService.get_or_create — меньше запросов

**Оценка:** 1 час

---

## 22. Кэширование list_defaults

**Оценка:** 5 мин

---

## 23. Батч-запросы в интеграции

**Оценка:** 1 час

---

## 24. Недостающие индексы для JOIN-полей

**Оценка:** 15 мин

---

## 25. Check constraints для остатков

**Оценка:** 15 мин

---

# ЧАСТЬ 5: ДОПОЛНИТЕЛЬНЫЕ ЗАДАЧИ

## 26. Единый стиль маршрутов API

**Проблема:** Одни сущности с префиксом, другие без.

**Оценка:** 1-2 часа

---

## 27. Единый метод обновления (PATCH)

**Оценка:** 30 мин

---

## 28. REST-семантика для action-роутов

**Оценка:** 1 час

---

## 29. Поиск и фильтрация в list-роутах

**Оценка:** 2-3 часа

---

## 30. Refresh token + Logout

**Оценка:** 2-3 часа

---

## 31. Bulk-операции

**Оценка:** 1-2 часа

---

## 32. Вебхуки

**Оценка:** 3-4 часа

---

## 33. Health check + Metrics

**Оценка:** 1 час

---

## 34. Dev/Prod конфигурация

**Оценка:** 30 мин

---

## 35. Seed-данные

**Оценка:** 1 час

---

# ИТОГОВАЯ ОЦЕНКА

| Часть | Задачи | Оценка |
|-------|--------|--------|
| P0 | 5 задач | 6 часов |
| P1 | 7 задач | 8 часов |
| P2 (архитектура) | 7 задач | 11 часов |
| P2 (оптимизация) | 6 задач | 3 часа |
| P2 (дополнительно) | 10 задач | 14 часов |
| **Итого** | **35 задач** | **42 часа** |

---

# ПОРЯДОК РЕАЛИЗАЦИИ

1. P0: Обработка ошибок flush/commit (1)
2. P0: Pydantic-валидация (2)
3. P0: Безопасность файлов, JWT, rate limiting (3,4,5)
4. P1: selectinload (6)
5. P1: Логирование, каскадное удаление (9,10)
6. P1: Конкурентность, утечки ресурсов (11,12)
7. P2: Архитектура — BaseRepository, DI, сервисы (13-19)
8. P2: Оптимизации (20-25)
9. P2: Дополнительные (26-35)

---

# КРИТЕРИИ ПРИЁМКИ

- [ ] Все session.flush/commit обёрнуты в try/except
- [ ] Нет body: dict без Pydantic-схемы
- [ ] Все list-роуты используют selectinload
- [ ] Все except-блоки имеют логирование
- [ ] Каскадное удаление для всех связей
- [ ] SELECT FOR UPDATE при изменении остатков
- [ ] Файлы проверяются на тип и размер
- [ ] Rate limiting на auth-эндпоинтах
- [ ] Бизнес-логика вынесена из роутов
- [ ] Единый BaseRepository
- [ ] DI через Depends()
- [ ] Единый формат ответов API
- [ ] Недостающие индексы созданы
- [ ] Check constraints на остатки
- [ ] Единый стиль маршрутов
- [ ] Единый метод обновления
- [ ] REST-семантика
- [ ] Поиск и фильтрация в list-роутах
- [ ] Refresh token + logout
- [ ] Bulk-операции
- [ ] Вебхуки
- [ ] Health check + metrics
- [ ] Dev/prod конфигурация
- [ ] Seed-данные
