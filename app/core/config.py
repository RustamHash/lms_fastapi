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

    jwt_secret_key: str = Field(..., description="Секрет JWT")
    jwt_algorithm: str = Field(default="HS256")
    access_token_expire_minutes: int = Field(default=1440)

    dadata_token: str | None = Field(default=None)
    dadata_secret: str | None = Field(default=None)

    geosuggest_api_key: str | None = Field(default=None)

    log_level: str = Field(default="INFO")
    debug_sql: bool = Field(default=False)
    app_log_file_path: str = Field(default="logs/app.log")
    error_log_file_path: str = Field(default="logs/error.log")
    sql_log_file_path: str = Field(default="logs/sql.log")


@lru_cache
def get_settings() -> Settings:
    return Settings()
