"""Тесты импорта резюме в сервисе."""

from types import SimpleNamespace
from unittest.mock import AsyncMock
from uuid import uuid4

import pytest

from app.core.exceptions import ValidationException
from app.schemas.resume_import import ImportedResumeSchema
from app.services.resume import ResumeService


def imported_resume() -> ImportedResumeSchema:
    """Возвращает данные импортированного резюме."""
    return ImportedResumeSchema.model_validate(
        {
            "title": "Imported resume",
            "sections": [
                {"section_type": "summary", "content": {"text": "Developer"}},
                {"section_type": "skills", "content": {"skills": [{"name": "Python"}]}},
            ],
        }
    )


@pytest.mark.asyncio
async def test_import_creates_sections_in_parser_order() -> None:
    """Создаёт секции в порядке ответа парсера."""
    resume = SimpleNamespace(id=uuid4())
    repository = SimpleNamespace(
        create_resume=AsyncMock(return_value=resume),
        add_section=AsyncMock(),
        get_resume_with_sections=AsyncMock(return_value=resume),
        session=SimpleNamespace(commit=AsyncMock(), rollback=AsyncMock()),
    )
    extractor = SimpleNamespace(extract=lambda _name, _data: "source text")
    parser = SimpleNamespace(parse=AsyncMock(return_value=imported_resume()))
    service = ResumeService(repository, extractor=extractor, parser=parser)

    result = await service.import_resume(uuid4(), "resume.docx", b"content")

    assert result is resume
    positions = [
        call.kwargs["position"] for call in repository.add_section.await_args_list
    ]
    section_types = [
        call.kwargs["section_type"].value
        for call in repository.add_section.await_args_list
    ]
    assert positions == [0, 1]
    assert section_types == [
        "summary",
        "skills",
    ]
    repository.session.commit.assert_awaited_once_with()


@pytest.mark.asyncio
async def test_import_rolls_back_when_parser_fails() -> None:
    """Откатывает транзакцию при ошибке AI-парсера."""
    repository = SimpleNamespace(
        session=SimpleNamespace(commit=AsyncMock(), rollback=AsyncMock()),
    )
    extractor = SimpleNamespace(extract=lambda _name, _data: "source text")
    parser = SimpleNamespace(
        parse=AsyncMock(side_effect=ValidationException("AI response is invalid"))
    )
    service = ResumeService(repository, extractor=extractor, parser=parser)

    with pytest.raises(ValidationException):
        await service.import_resume(uuid4(), "resume.docx", b"content")

    repository.session.rollback.assert_awaited_once_with()
