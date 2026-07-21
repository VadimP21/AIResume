"""Тесты импорта резюме в сервисе."""

from types import SimpleNamespace
from unittest.mock import ANY, AsyncMock
from uuid import uuid4

import pytest

from app.core.exceptions import ServiceUnavailableException, ValidationException
from app.dto.resumes import CreateResumeCommand, CreateSectionCommand
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
    repository.create_resume.assert_awaited_once_with(
        user_id=ANY,
        command=CreateResumeCommand(title="Imported resume"),
    )
    positions = [
        call.kwargs["position"] for call in repository.add_section.await_args_list
    ]
    commands = [
        call.kwargs["command"] for call in repository.add_section.await_args_list
    ]
    assert positions == [0, 1]
    assert commands == [
        CreateSectionCommand(
            section_type=section.section_type,
            content=section.content.model_dump(mode="json"),
        )
        for section in imported_resume().sections
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


@pytest.mark.asyncio
async def test_import_returns_service_unavailable_when_ai_is_not_configured() -> None:
    """Возвращает 503-сценарий, если активный AI-провайдер не настроен."""
    repository = SimpleNamespace(session=SimpleNamespace(rollback=AsyncMock()))
    extractor = SimpleNamespace(extract=lambda _name, _data: "source text")
    service = ResumeService(repository, extractor=extractor, parser=None)

    with pytest.raises(ServiceUnavailableException, match="temporarily unavailable"):
        await service.import_resume(uuid4(), "resume.docx", b"content")

    repository.session.rollback.assert_not_awaited()
