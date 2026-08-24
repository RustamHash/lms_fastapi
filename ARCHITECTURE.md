# Архитектура LMS FastAPI

## Слои приложения

HTTP Request -> Router -> Service -> Repository -> Database

---

## Router (app/api/v1/*/routes.py)

### Может:
- Принимать HTTP-запросы
- Валидировать входные данные (Pydantic-схемы)
- Вызывать сервис через Depends()
- Возвращать Pydantic-схемы (model_validate)
- Проверять права (require_permission)

### Не может:
- Делать SQL-запросы (select, session.scalar)
- Вызывать репозитории напрямую
- Создавать сервисы вручную (ProductService(ProductRepository(session)))
- Работать с session напрямую (session.add, session.flush)
- Содержать бизнес-логику

### Шаблон:
@router.get("/products", response_model=list[ProductRead])
async def list_products(service: ProductService = Depends(get_product_service)):
    rows = await service.list_all()
    return [ProductRead.model_validate(r) for r in rows]

---

## Service (app/*/services/*.py)

### Может:
- Содержать бизнес-логику
- Вызывать репозиторий (через self._repo)
- Валидировать бизнес-правила
- Вызывать другие сервисы
- Отправлять события (event_bus)

### Не может:
- Делать SQL-запросы напрямую (select, session.scalar)
- Работать с session напрямую
- Использовать FastAPI-зависимости (Depends, Request)
- Возвращать HTTP-ответы

### Шаблон:
class ProductService:
    def __init__(self, repo: ProductRepository):
        self._repo = repo

    async def list_all(self) -> list[Product]:
        return await self._repo.list_all()

    async def create(self, **kwargs) -> Product:
        # Бизнес-проверки
        if await self._repo.get_by_external_id(...):
            raise ValueError("Товар уже существует")
        return await self._repo.create(**kwargs)

---

## Repository (app/*/repository.py)

### Может:
- Делать SQL-запросы через SQLAlchemy
- Наследовать BaseRepository
- Переопределять методы для selectinload
- Добавлять специфичные методы (get_by_code, get_by_external_id)

### Не может:
- Содержать бизнес-логику
- Валидировать данные
- Вызывать другие репозитории
- Отправлять события

### Шаблон:
class ProductRepository(BaseRepository[Product]):
    def __init__(self, session: AsyncSession):
        super().__init__(session, Product)

    async def get_by_id(self, id: int) -> Product | None:
        stmt = select(Product).where(Product.id == id).options(selectinload(Product.group))
        return await self._s.scalar(stmt)

    async def get_by_external_id(self, depositor_id: int, external_id: str):
        stmt = select(Product).where(...)
        return await self._s.scalar(stmt)

---

## Dependency Injection (app/api/dependencies.py)

### Правила:
1. Все фабрики сервисов в этом файле
2. Фабрика = функция, возвращающая сервис
3. Роут получает сервис через Depends()

### Шаблон:
def get_product_service(session: AsyncSession = Depends(get_session)) -> ProductService:
    return ProductService(ProductRepository(session))

---

## Pydantic-схемы (app/api/v1/*/schemas.py)

### Правила:
1. Read-схемы содержат вложенные объекты
2. Create-схемы содержат ID, не объекты
3. Update-схемы содержат optional-поля
4. Все схемы в schemas.py, не в routes.py

### Шаблон:
class ProductRead(BaseRead):
    name: str
    group: ProductGroupRead | None = None  # вложенная

class ProductCreate(BaseModel):
    group_id: int  # ID, не объект

class ProductUpdate(BaseModel):
    name: str | None = None

---

## BaseRepository (app/infrastructure/base_repository.py)

### Методы:
- get_by_id(id) -> ModelType | None
- get_by_ids(ids) -> list[ModelType]
- list_all() -> list[ModelType]
- create(**kwargs) -> ModelType
- update(id, **kwargs) -> ModelType | None
- soft_delete(id, user_id) -> bool
- restore(id, user_id) -> bool

### Правила:
1. Наследовать во всех репозиториях
2. Переопределять только при необходимости (selectinload)
3. Использовать параметр id (не user_id, address_id)
4. Не добавлять бизнес-логику

---

## Запрещённые паттерны

1. SQL в роутах: select(), session.scalar(), session.execute()
2. session.add/flush/commit в роутах
3. Создание сервисов вручную: ProductService(ProductRepository(session))
4. Прямой вызов репозитория из роута
5. Pydantic-схемы в routes.py
6. body: dict — всегда Pydantic-схема
7. Ручная сборка ответов — всегда model_validate()

---

## Порядок исправления

### Шаг 1: Репозитории
- Все на BaseRepository
- Параметр id вместо user_id, address_id
- selectinload для связей

### Шаг 2: Сервисы
- Единый стиль методов
- Бизнес-логика в сервисах
- Валидация в сервисах

### Шаг 3: Dependency Injection
- Фабрики в app/api/dependencies.py
- Роуты через Depends()

### Шаг 4: Роуты
- Только Depends(service)
- model_validate вместо ручной сборки
- Pydantic вместо dict

### Шаг 5: Проверка
- pyright: 0 errors
- Все роуты без session
- Все роуты без Repository
