"""Тесты AI-парсера резюме."""

from unittest.mock import AsyncMock

import pytest

from app.core.exceptions import ServiceUnavailableException, ValidationException
from app.services.ai.exceptions import AIProviderError
from app.services.resume_ai_parser import ResumeAIParser


def valid_response() -> str:
    """Возвращает валидный ответ модели."""
    return """{
        "title": "Python Developer",
        "sections": [
            {"section_type": "summary", "content": {"text": "Backend developer"}},
            {
                "section_type": "skills",
                "content": {"skills": [{"name": "Python", "level": "senior"}]}
            }
        ]
    }"""


@pytest.mark.asyncio
async def test_parses_valid_structured_model_response() -> None:
    """Преобразует валидный ответ модели в DTO."""
    client = AsyncMock()
    client.provider = "gemini"
    client.model = "test-model"
    client.generate_json.return_value = valid_response()
    parser = ResumeAIParser(client=client)

    result = await parser.parse("resume text")

    assert result.title == "Python Developer"
    assert [section.section_type.value for section in result.sections] == [
        "summary",
        "skills",
    ]


@pytest.mark.asyncio
async def test_rejects_invalid_model_response() -> None:
    """Отклоняет ответ модели, не соответствующий контракту."""
    client = AsyncMock()
    client.provider = "gemini"
    client.model = "test-model"
    client.generate_json.return_value = "{}"
    parser = ResumeAIParser(client=client)

    with pytest.raises(ValidationException, match="AI response"):
        await parser.parse("resume text")


@pytest.mark.asyncio
async def test_rejects_empty_model_response() -> None:
    """Отклоняет пустой ответ модели как некорректный JSON."""
    client = AsyncMock()
    client.provider = "gemini"
    client.model = "test-model"
    client.generate_json.return_value = ""
    parser = ResumeAIParser(client=client)

    with pytest.raises(ValidationException, match="AI response"):
        await parser.parse("resume text")


@pytest.mark.asyncio
@pytest.mark.parametrize("category", ["authentication", "timeout", "unavailable"])
async def test_maps_provider_error_to_service_unavailable(category: str) -> None:
    """Преобразует ошибку провайдера в безопасный ответ 503."""
    client = AsyncMock()
    client.provider = "gemini"
    client.model = "test-model"
    client.generate_json.side_effect = AIProviderError(category)
    parser = ResumeAIParser(client=client)

    with pytest.raises(ServiceUnavailableException, match="temporarily unavailable"):
        await parser.parse("resume text")
