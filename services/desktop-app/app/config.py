"""Desktop App — Configuration."""
from __future__ import annotations

import os
from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )

    KUBECONFIG: str = ""
    K8S_NAMESPACE: str = "default"
    REFRESH_INTERVAL_SECONDS: int = 15
    LOG_LEVEL: str = "INFO"


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings: Settings = get_settings()
