"""Создаёт AI-клиент выбранного в конфигурации провайдера."""

from pydantic import SecretStr

from app.core.config import Settings
from app.services.ai.clients import (
    DeepSeekAIClient,
    GeminiAIClient,
    GigaChatAIClient,
)
from app.services.ai.exceptions import AIConfigurationError
from app.services.ai.protocols import ResumeAIClient


def create_ai_client(settings: Settings) -> ResumeAIClient:
    """Создаёт клиент только активного AI-провайдера."""
    if settings.AI_PROVIDER == "gemini":
        return GeminiAIClient(
            api_key=_get_secret(settings.GEMINI_API_KEY, "gemini"),
            model=_get_model(settings.GEMINI_MODEL, "gemini"),
            timeout_seconds=settings.AI_REQUEST_TIMEOUT_SECONDS,
        )
    if settings.AI_PROVIDER == "deepseek":
        return DeepSeekAIClient(
            api_key=_get_secret(settings.DEEPSEEK_API_KEY, "deepseek"),
            model=_get_model(settings.DEEPSEEK_MODEL, "deepseek"),
            base_url=settings.DEEPSEEK_BASE_URL,
            timeout_seconds=settings.AI_REQUEST_TIMEOUT_SECONDS,
        )
    return GigaChatAIClient(
        auth_key=_get_secret(settings.GIGACHAT_AUTH_KEY, "gigachat"),
        model=_get_model(settings.GIGACHAT_MODEL, "gigachat"),
        base_url=settings.GIGACHAT_BASE_URL,
        timeout_seconds=settings.AI_REQUEST_TIMEOUT_SECONDS,
    )


def _get_secret(value: SecretStr | None, provider: str) -> str:
    """Возвращает непустой секрет выбранного провайдера."""
    if value is None:
        raise AIConfigurationError(provider)
    secret = value.get_secret_value()
    if not secret:
        raise AIConfigurationError(provider)
    return secret


def _get_model(value: str | None, provider: str) -> str:
    """Возвращает непустую модель выбранного провайдера."""
    if value is None or not value.strip():
        raise AIConfigurationError(provider)
    return value
