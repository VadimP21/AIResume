from functools import lru_cache
from typing import Literal

from pydantic import computed_field, model_validator, field_validator, RedisDsn, PostgresDsn
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
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
        "staging",
        "production",
    ] = "development"

    DEBUG: bool = False

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
        if len(value) < 32:
            raise ValueError(
                "JWT_SECRET must contain at least 32 characters"
            )
        return value

    @model_validator(mode="after")
    def validate_environment(self):
        if self.APP_ENV == "production" and self.DEBUG:
            raise ValueError("DEBUG must be False in production")
        return self
    # =========================================================
    # COMPUTED FIELDS
    # =========================================================

    @computed_field
    @property
    def ASYNC_DATABASE_URL(self) -> PostgresDsn:
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
        return RedisDsn(
            f"redis://:"
            f"{self.REDIS_PASSWORD}@"
            f"{self.REDIS_HOST}:"
            f"{self.REDIS_PORT}/0"
        )


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
