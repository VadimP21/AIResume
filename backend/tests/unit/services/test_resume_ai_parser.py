"""Тесты AI-парсера резюме."""

from unittest.mock import AsyncMock

import pytest

from app.core.exceptions import ValidationException
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
    client.chat.completions.create.return_value.choices = [
        type(
            "Choice",
            (),
            {"message": type("Message", (), {"content": valid_response()})()},
        )()
    ]
    parser = ResumeAIParser(client=client, model="test-model")

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
    client.chat.completions.create.return_value.choices = [
        type("Choice", (), {"message": type("Message", (), {"content": "{}"})()})()
    ]
    parser = ResumeAIParser(client=client, model="test-model")

    with pytest.raises(ValidationException, match="AI response"):
        await parser.parse("resume text")


@pytest.mark.asyncio
async def test_hides_provider_error() -> None:
    """Не раскрывает техническую ошибку провайдера."""
    client = AsyncMock()
    client.chat.completions.create.side_effect = RuntimeError("provider secret")
    parser = ResumeAIParser(client=client, model="test-model")

    with pytest.raises(ValidationException, match="Unable to parse resume"):
        await parser.parse("resume text")
