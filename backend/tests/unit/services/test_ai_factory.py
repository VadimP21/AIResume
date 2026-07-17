"""Тестирует фабрику выбора AI-провайдера."""

import pytest

from app.core.config import Settings
from app.services.ai.clients import DeepSeekAIClient, GeminiAIClient, GigaChatAIClient
from app.services.ai.exceptions import AIConfigurationError
from app.services.ai.factory import create_ai_client


def make_settings(**values: object) -> Settings:
    """Создаёт минимальные настройки для теста AI-фабрики."""
    data: dict[str, object] = {
        "POSTGRES_HOST": "localhost",
        "POSTGRES_DB": "test",
        "POSTGRES_USER": "test",
        "POSTGRES_PASSWORD": "test",
        "REDIS_HOST": "localhost",
        "REDIS_PASSWORD": "test",
        "JWT_SECRET": "x" * 32,
    }
    data.update(values)
    return Settings.model_validate(data)


@pytest.mark.parametrize(
    ("provider", "settings_values", "expected_type"),
    [
        (
            "gemini",
            {"GEMINI_API_KEY": "key", "GEMINI_MODEL": "gemini-test"},
            GeminiAIClient,
        ),
        (
            "deepseek",
            {"DEEPSEEK_API_KEY": "key", "DEEPSEEK_MODEL": "deepseek-test"},
            DeepSeekAIClient,
        ),
        (
            "gigachat",
            {"GIGACHAT_AUTH_KEY": "key", "GIGACHAT_MODEL": "GigaChat-Test"},
            GigaChatAIClient,
        ),
    ],
)
def test_factory_creates_only_selected_provider(
    provider: str,
    settings_values: dict[str, str],
    expected_type: type[object],
) -> None:
    """Создаёт адаптер только выбранного провайдера."""
    client = create_ai_client(make_settings(AI_PROVIDER=provider, **settings_values))

    assert isinstance(client, expected_type)


def test_factory_rejects_missing_selected_provider_configuration() -> None:
    """Отклоняет запуск выбранного провайдера без обязательного ключа."""
    with pytest.raises(AIConfigurationError, match="gemini"):
        create_ai_client(make_settings(AI_PROVIDER="gemini"))
