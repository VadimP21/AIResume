"""Содержит компоненты модуля config."""

from functools import lru_cache
from typing import Literal

from pydantic import (
    EmailStr,
    PostgresDsn,
    RedisDsn,
    SecretStr,
    computed_field,
    field_validator,
    model_validator,
)
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Представляет сущность Settings."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # =========================================================
    # APP
    # =========================================================

    APP_NAME: str = "resume-builder"

    APP_ENV: Literal[
        "development",
        "test",
        "staging",
        "production",
    ] = "development"

    DEBUG: bool = False
    ENABLE_FAKE_AUTH: bool = False
    FAKE_AUTH_EMAIL: EmailStr | None = None
    FAKE_AUTH_PASSWORD: SecretStr | None = None

    API_V1_PREFIX: str = "/api/v1"

    BACKEND_HOST: str = "0.0.0.0"
    BACKEND_PORT: int = 8000

    LOG_LEVEL: Literal[
        "DEBUG",
        "INFO",
        "WARNING",
        "ERROR",
        "CRITICAL",
    ] = "INFO"

    TIMEZONE: str = "UTC"

    # =========================================================
    # POSTGRES
    # =========================================================

    POSTGRES_HOST: str
    POSTGRES_PORT: int = 5432
    POSTGRES_DB: str
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str

    DB_POOL_SIZE: int = 20
    DB_MAX_OVERFLOW: int = 10
    DB_POOL_TIMEOUT: int = 30
    DB_POOL_RECYCLE: int = 1800

    # =========================================================
    # REDIS
    # =========================================================

    REDIS_HOST: str
    REDIS_PORT: int = 6379
    REDIS_PASSWORD: str

    # =========================================================
    # JWT
    # =========================================================

    JWT_SECRET: str
    JWT_ALGORITHM: str = "HS256"

    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    JWT_REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    REFRESH_TOKEN_EXPIRE_SECONDS: int = 604800
    JWT_ISSUER: str = "airesume-api"
    JWT_AUDIENCE: str = "airesume-client"
    # =========================================================
    # CORS
    # =========================================================

    CORS_ORIGINS: list[str] = [
        "http://localhost:3000",
    ]

    # =========================================================
    # VALIDATORS
    # =========================================================

    @field_validator("JWT_SECRET")
    @classmethod
    def validate_jwt_secret(cls, value: str) -> str:
        """Проверяет jwt secret."""
        if len(value) < 32:
            raise ValueError("JWT_SECRET must contain at least 32 characters")
        return value

    @model_validator(mode="after")
    def validate_environment(self):
        """Проверяет environment."""
        if self.APP_ENV == "production" and self.DEBUG:
            raise ValueError("DEBUG must be False in production")

        if self.ENABLE_FAKE_AUTH:
            if self.APP_ENV not in {"development", "test"}:
                raise ValueError(
                    "ENABLE_FAKE_AUTH is allowed only in development or test"
                )
            if self.FAKE_AUTH_EMAIL is None or self.FAKE_AUTH_PASSWORD is None:
                raise ValueError(
                    "FAKE_AUTH_EMAIL and FAKE_AUTH_PASSWORD are required "
                    "when ENABLE_FAKE_AUTH is enabled"
                )
            if not self.FAKE_AUTH_PASSWORD.get_secret_value():
                raise ValueError("FAKE_AUTH_PASSWORD must not be empty")
        return self

    @property
    def fake_auth_enabled(self) -> bool:
        """Выполняет операцию fake auth enabled."""
        return self.ENABLE_FAKE_AUTH and self.APP_ENV in {"development", "test"}

    def get_fake_auth_credentials(self) -> tuple[str, str]:
        """Возвращает fake auth credentials."""
        if (
            not self.fake_auth_enabled
            or self.FAKE_AUTH_EMAIL is None
            or self.FAKE_AUTH_PASSWORD is None
        ):
            raise RuntimeError("Fake auth is not configured")

        return str(self.FAKE_AUTH_EMAIL), self.FAKE_AUTH_PASSWORD.get_secret_value()

    # =========================================================
    # COMPUTED FIELDS
    # =========================================================

    @computed_field
    @property
    def ASYNC_DATABASE_URL(self) -> PostgresDsn:
        """Выполняет операцию ASYNC DATABASE URL."""
        return PostgresDsn(
            f"postgresql+asyncpg://"
            f"{self.POSTGRES_USER}:"
            f"{self.POSTGRES_PASSWORD}@"
            f"{self.POSTGRES_HOST}:"
            f"{self.POSTGRES_PORT}/"
            f"{self.POSTGRES_DB}"
        )

    @computed_field
    @property
    def DATABASE_URL(self) -> PostgresDsn:
        """Выполняет операцию DATABASE URL."""
        return PostgresDsn(
            f"postgresql+psycopg://"
            f"{self.POSTGRES_USER}:"
            f"{self.POSTGRES_PASSWORD}@"
            f"{self.POSTGRES_HOST}:"
            f"{self.POSTGRES_PORT}/"
            f"{self.POSTGRES_DB}"
        )

    @computed_field
    @property
    def REDIS_URL(self) -> RedisDsn:
        """Выполняет операцию REDIS URL."""
        return RedisDsn(
            f"redis://:{self.REDIS_PASSWORD}@{self.REDIS_HOST}:{self.REDIS_PORT}/0"
        )


@lru_cache
def get_settings() -> Settings:
    """Возвращает settings."""
    return Settings()


settings = get_settings()
