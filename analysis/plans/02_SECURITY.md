# ДЕТАЛЬНЫЙ ПЛАН: Безопасность

## 📍 Текущая проблема

### 2.1 Открытая регистрация
**Файл:** app/api/v1/accounts/routes.py

Любой может зарегистрироваться через POST /auth/register без проверки прав.

**Влияние:** Неавторизованный доступ к системе.

### 2.2 Отсутствие rate limiting
**Файл:** app/main.py

Нет ограничений на количество запросов к /auth/token.

**Влияние:** Возможность brute-force атак.

### 2.3 Нет CORS
**Файл:** app/main.py

**Влияние:** Браузер блокирует запросы с других доменов.

### 2.4 Права не проверяются
**Файл:** Все роуты

Функция require_permission() определена, но НЕ используется в роутах.

**Влияние:** Любой авторизованный пользователь может выполнять любые действия.

### 2.5 Слабые пароли
**Файл:** app/api/v1/accounts/schemas.py

Пароль: min_length=8, без требований к сложности.

**Влияние:** Легко подбираемые пароли.

### 2.6 Подделка audit-полей
**Файл:** Все роуты

created_by_id и updated_by_id могут быть переданы в body запроса.

**Влияние:** Фальсификация авторства действий.

## 💡 Варианты решения

### Вариант A: Быстрые фиксы
Только CORS + rate limiting через middleware
- **Плюсы:** Быстро (2 часа)
- **Минусы:** Не решает все проблемы
- **Сложность:** Низкая
- **Влияние:** Среднее

### Вариант B: Полная система прав
Реализовать RBAC с проверкой прав в каждом роуте
- **Плюсы:** Полная безопасность
- **Минусы:** Много изменений (2-3 дня)
- **Сложность:** Высокая
- **Влияние:** Высокое

### Вариант C: Комплексный подход
CORS + rate limiting + валидация паролей + базовые проверки прав
- **Плюсы:** Хорошее покрытие
- **Минусы:** Нужно тестировать (1-2 дня)
- **Сложность:** Средняя
- **Влияние:** Высокое

## 🔧 Рекомендуемое решение

**Вариант C** — поэтапное внедрение.

## 📝 Шаги реализации

### CORS
1. [ ] Добавить в Settings: allowed_origins: list[str] = ["http://localhost:3000"]
2. [ ] В main.py добавить CORSMiddleware

### Rate Limiting
3. [ ] Установить slowapi: pip install slowapi
4. [ ] Настроить лимиты: 5/minute для /auth/token, 3/hour для /auth/register
5. [ ] Добавить SlowAPIMiddleware в main.py

### Валидация паролей
6. [ ] В UserCreate добавить pattern для сложности пароля (минимум 1 буква, 1 цифра, 1 спецсимвол)

### Проверка прав
7. [ ] В роутах заменить UserDep на Depends(require_permission("action:entity"))
8. [ ] Пример: @router.post("/products", dependencies=[Depends(require_permission("create:products"))])

### Защита audit-полей
9. [ ] Убрать created_by_id/updated_by_id из Pydantic схем
10. [ ] Всегда брать из Depends(get_current_user_id)

### Закрытие регистрации
11. [ ] Убрать публичный POST /auth/register
12. [ ] Добавить POST /users с Depends(require_permission("create:users"))

## 🧪 Как проверить

Проверить CORS:
curl -X OPTIONS http://localhost:8000/api/v1/auth/token -H "Origin: http://localhost:3000" -H "Access-Control-Request-Method: POST" -v

Проверить rate limiting (6 запросов, последний должен вернуть 429):
for i in {1..6}; do curl -X POST http://localhost:8000/api/v1/auth/token -d "username=test&password=wrong" -s -o /dev/null -w "%{http_code}\n"; done

Проверить валидацию пароля (должен вернуть 422):
curl -X POST http://localhost:8000/api/v1/auth/register -H "Content-Type: application/json" -d '{"username":"test","password":"weak","phone":"","email":""}'

Проверить права (должен вернуть 403):
curl -X POST http://localhost:8000/api/v1/products -H "Authorization: Bearer TOKEN" -H "Content-Type: application/json" -d '{"depositor_id":1,"external_id":"test","name":"Test"}'

## 📚 Связанные файлы

- app/main.py
- app/api/v1/accounts/routes.py
- app/api/v1/accounts/schemas.py
- app/core/dependencies.py
- app/core/config.py

## ⚠️ Риски

- Блокировка легитимных пользователей при rate limiting
- Поломка фронтенда при CORS
- Несовместимость с существующими токенами при изменении прав
