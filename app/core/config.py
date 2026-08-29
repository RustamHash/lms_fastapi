"""Конфигурация приложения."""

from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    database_url: str = Field(..., description="SQLAlchemy URL для подключения к БД")

    redis_url: str = Field(
        default="redis://localhost:6379/0",
        description="Redis: fallback для Celery broker",
    )
    celery_broker_url: str | None = Field(
        default=None,
        description="Celery broker; если пусто — redis_url",
    )
    celery_result_backend: str | None = Field(
        default=None,
        description="Celery result backend; если пусто — тот же host, DB /1",
    )

    jwt_secret_key: str = Field(..., description="Секрет JWT")
    jwt_algorithm: str = Field(default="HS256")
    access_token_expire_minutes: int = Field(default=1440)

    def resolve_celery_broker_url(self) -> str:
        return self.celery_broker_url or self.redis_url

    def resolve_celery_result_backend(self) -> str:
        if self.celery_result_backend:
            return self.celery_result_backend
        base = self.redis_url.rsplit("/", 1)[0]
        return f"{base}/1"

    dadata_token: str | None = Field(default=None)
    dadata_secret: str | None = Field(default=None)

    geosuggest_api_key: str | None = Field(default=None)

    cors_origins: list[str] = Field(
        default=["http://127.0.0.1:5173", "http://localhost:5173"],
        description="Разрешенные origins для CORS",
    )

    environment: str = Field(default="development", description="Окружение: development, production")
    log_level: str = Field(default="INFO")
    debug_sql: bool = Field(default=False)
    app_log_file_path: str = Field(default="logs/app.log")
    error_log_file_path: str = Field(default="logs/error.log")
    sql_log_file_path: str = Field(default="logs/sql.log")
    log_to_console: bool = Field(default=True, description="Логировать в консоль")
    log_to_file: bool = Field(default=True, description="Логировать в файл")
    log_json_format: bool = Field(default=False, description="Использовать JSON-формат для логов")


@lru_cache
def get_settings() -> Settings:
    return Settings()
