# LMS FastAPI

Документация: [docs/README.md](docs/README.md) (карта модулей). Слои: [ARCHITECTURE.md](ARCHITECTURE.md).

## Установка

python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt


## Миграции

alembic upgrade head
alembic revision --autogenerate -m "описание"

## Запуск

uvicorn app.main:app --reload --host 0.0.0.0 --port 8080

## Импорт

python scripts/import_from_ftp.py
python scripts/clear_orders.py
python scripts/bootstrap_users.py
python scripts/create_superuser.py admin password
python scripts/create_default_roles.py

## API

Swagger: http://localhost:8080/docs
OpenAPI: http://localhost:8080/openapi.json

## Логи

logs/app.log
logs/error.log
logs/sql.log
logs/emails/


# FastAPI
docker compose -f docker-compose.dev.yml logs fastapi -f

# Celery
docker compose -f docker-compose.dev.yml logs celery_worker -f

# Фронтенд
docker compose -f docker-compose.dev.yml logs frontend -f

# PostgreSQL
docker compose -f docker-compose.dev.yml logs postgres -f

# Redis
docker compose -f docker-compose.dev.yml logs redis -f



docker compose -f docker-compose.dev.yml logs -f