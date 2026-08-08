"""Flask Admin UI — Configuration."""
from __future__ import annotations

from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    FLASK_ENV: str = "development"
    FLASK_SECRET_KEY: str = "change_me_flask_secret_key"
    LOG_LEVEL: str = "INFO"

    FASTAPI_BASE_URL: str = "http://localhost:8000"
    ADMIN_USERNAME: str = "admin"
    ADMIN_PASSWORD: str = "admin_password"


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings: Settings = get_settings()
