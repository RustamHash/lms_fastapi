# LMS FastAPI

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
