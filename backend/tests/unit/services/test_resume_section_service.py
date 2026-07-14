"""Содержит компоненты модуля test_resume_section_service."""

from types import SimpleNamespace
from unittest.mock import AsyncMock
from uuid import uuid4

import pytest

from app.models.resume_section import SectionType
from app.schemas.resume import ResumeSectionCreateSchema
from app.schemas.section import SummaryContent, SummarySection
from app.services.resume import ResumeService


def make_data() -> ResumeSectionCreateSchema:
    """Создаёт data."""
    return ResumeSectionCreateSchema(
        section=SummarySection(
            section_type=SectionType.SUMMARY,
            content=SummaryContent(text="Summary"),
        ),
    )


def make_repository(position: int | None) -> SimpleNamespace:
    """Создаёт repository."""
    section = SimpleNamespace(id=uuid4())
    session = SimpleNamespace(
        commit=AsyncMock(), refresh=AsyncMock(), rollback=AsyncMock()
    )
    return SimpleNamespace(
        get_next_position_and_lock_resume=AsyncMock(return_value=position),
        add_section=AsyncMock(return_value=section),
        session=session,
    )


@pytest.mark.asyncio
async def test_add_section_uses_first_position() -> None:
    """Проверяет сценарий add section uses first position."""
    repository = make_repository(position=1)
    service = ResumeService(repository)
    resume_id = uuid4()
    user_id = uuid4()

    section = await service.add_section(resume_id, user_id, make_data())

    assert section is repository.add_section.return_value
    repository.add_section.assert_awaited_once_with(
        resume_id=resume_id,
        section_type=SectionType.SUMMARY,
        content=SummaryContent(text="Summary"),
        position=1,
    )
    repository.session.commit.assert_awaited_once_with()


@pytest.mark.asyncio
async def test_add_section_rolls_back_when_commit_fails() -> None:
    """Проверяет сценарий add section rolls back when commit fails."""
    repository = make_repository(position=2)
    repository.session.commit.side_effect = RuntimeError("commit failed")
    service = ResumeService(repository)

    with pytest.raises(RuntimeError, match="commit failed"):
        await service.add_section(uuid4(), uuid4(), make_data())

    repository.session.rollback.assert_awaited_once_with()
