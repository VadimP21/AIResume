"""Тестирует зависимости AI-парсера резюме."""

from app.api.v1.resumes import dependencies
from app.core.config import Settings


def make_settings() -> Settings:
    """Создаёт настройки GigaChat для теста singleton-зависимости."""
    return Settings.model_validate(
        {
            "POSTGRES_HOST": "localhost",
            "POSTGRES_DB": "test",
            "POSTGRES_USER": "test",
            "POSTGRES_PASSWORD": "test",
            "REDIS_HOST": "localhost",
            "REDIS_PASSWORD": "test",
            "JWT_SECRET": "x" * 32,
            "AI_PROVIDER": "gigachat",
            "GIGACHAT_AUTH_KEY": "key",
            "GIGACHAT_MODEL": "GigaChat-Test",
        }
    )


def test_resume_ai_dependency_reuses_client_in_process(monkeypatch) -> None:
    """Возвращает один GigaChat-клиент для последовательных зависимостей."""
    monkeypatch.setattr(dependencies, "settings", make_settings())
    dependencies.get_resume_ai_client.cache_clear()
    try:
        first_parser = dependencies.get_resume_ai_parser()
        second_parser = dependencies.get_resume_ai_parser()

        assert first_parser.client is second_parser.client
    finally:
        dependencies.get_resume_ai_client.cache_clear()
