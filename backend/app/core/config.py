from functools import lru_cache
from typing import Literal

from pydantic import computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )

    # =========================================================
    # APP
    # =========================================================

    APP_NAME: str = "resume-builder"

    APP_ENV: Literal[
        "development",
        "staging",
        "production",
    ] = "development"

    DEBUG: bool = True

    API_V1_PREFIX: str = "/api/v1"

    BACKEND_HOST: str = "0.0.0.0"
    BACKEND_PORT: int = 8000

    LOG_LEVEL: str = "INFO"

    # =========================================================
    # POSTGRES
    # =========================================================

    POSTGRES_HOST: str
    POSTGRES_PORT: int = 5432
    POSTGRES_DB: str
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str

    # =========================================================
    # REDIS
    # =========================================================

    REDIS_HOST: str
    REDIS_PORT: int = 6379

    # =========================================================
    # JWT
    # =========================================================

    JWT_SECRET: str
    JWT_ALGORITHM: str = "HS256"

    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    JWT_REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # =========================================================
    # CORS
    # =========================================================

    CORS_ORIGINS: list[str] = []

    # =========================================================
    # COMPUTED FIELDS
    # =========================================================

    @computed_field
    @property
    def DATABASE_URL(self) -> str:
        return (
            f"postgresql+asyncpg://"
            f"{self.POSTGRES_USER}:"
            f"{self.POSTGRES_PASSWORD}@"
            f"{self.POSTGRES_HOST}:"
            f"{self.POSTGRES_PORT}/"
            f"{self.POSTGRES_DB}"
        )

    @computed_field
    @property
    def REDIS_URL(self) -> str:
        return (
            f"redis://"
            f"{self.REDIS_HOST}:"
            f"{self.REDIS_PORT}/0"
        )


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
