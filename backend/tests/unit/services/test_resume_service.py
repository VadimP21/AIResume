"""Содержит компоненты модуля test_resume_service."""

from datetime import UTC, datetime
from types import SimpleNamespace
from unittest.mock import ANY, AsyncMock
from uuid import uuid4

import pytest

from app.dto.resumes import (
    CreateResumeCommand,
    CreateSectionCommand,
    ResumeDTO,
    SectionType,
    UpdateResumeCommand,
)
from app.services.resume import ResumeService


def make_repository(resume: object) -> SimpleNamespace:
    """Создаёт repository."""
    session = SimpleNamespace(
        delete=AsyncMock(),
        flush=AsyncMock(),
        commit=AsyncMock(),
        rollback=AsyncMock(),
    )
    return SimpleNamespace(
        delete_resume=AsyncMock(return_value=resume is not None),
        session=session,
    )


@pytest.mark.asyncio
async def test_delete_resume_commits_transaction() -> None:
    """Проверяет сценарий delete resume commits transaction."""
    resume = object()
    repository = make_repository(resume)
    service = ResumeService(repository)
    resume_id = uuid4()
    user_id = uuid4()

    await service.delete_resume(resume_id, user_id)

    repository.delete_resume.assert_awaited_once_with(resume_id, user_id)
    repository.session.flush.assert_awaited_once_with()
    repository.session.commit.assert_awaited_once_with()
    repository.session.rollback.assert_not_awaited()


@pytest.mark.asyncio
async def test_delete_resume_rolls_back_when_commit_fails() -> None:
    """Проверяет сценарий delete resume rolls back when commit fails."""
    resume = object()
    repository = make_repository(resume)
    repository.session.commit.side_effect = RuntimeError("commit failed")
    service = ResumeService(repository)

    with pytest.raises(RuntimeError, match="commit failed"):
        await service.delete_resume(uuid4(), uuid4())

    repository.session.rollback.assert_awaited_once_with()


@pytest.mark.asyncio
async def test_create_resume_creates_snapshot_in_same_transaction() -> None:
    """Проверяет создание snapshot вместе с резюме."""
    now = datetime.now(UTC)
    resume = ResumeDTO(
        id=uuid4(),
        user_id=uuid4(),
        title="Resume",
        created_at=now,
        updated_at=now,
        sections=(),
    )
    repository = SimpleNamespace(
        create_resume=AsyncMock(return_value=resume),
        get_resume_with_sections=AsyncMock(return_value=resume),
        session=SimpleNamespace(commit=AsyncMock(), rollback=AsyncMock()),
    )
    versioning = SimpleNamespace(create_snapshot=AsyncMock())
    service = ResumeService(repository, versioning=versioning)

    await service.create_resume(uuid4(), SimpleNamespace(title="Resume"))

    repository.create_resume.assert_awaited_once_with(
        user_id=ANY,
        command=CreateResumeCommand(title="Resume"),
    )
    versioning.create_snapshot.assert_awaited_once_with(resume)
    repository.session.commit.assert_awaited_once_with()


@pytest.mark.asyncio
async def test_restore_version_saves_current_state_before_replacing_sections() -> None:
    """Проверяет сохранение текущего состояния перед восстановлением."""
    resume_id = uuid4()
    version_id = uuid4()
    user_id = uuid4()
    now = datetime.now(UTC)
    resume = ResumeDTO(
        id=resume_id,
        user_id=user_id,
        title="Current",
        created_at=now,
        updated_at=now,
        sections=(),
    )
    version = SimpleNamespace(
        snapshot={
            "resume": {"id": str(resume_id), "title": "Previous"},
            "sections": [
                {
                    "id": str(uuid4()),
                    "type": "summary",
                    "position": 1,
                    "content": {"text": "Restored"},
                }
            ],
        }
    )
    repository = SimpleNamespace(
        get_resume_with_sections=AsyncMock(return_value=resume),
        restore_resume=AsyncMock(return_value=resume),
        session=SimpleNamespace(commit=AsyncMock(), rollback=AsyncMock()),
    )
    versioning = SimpleNamespace(create_snapshot=AsyncMock())
    service = ResumeService(repository, versioning=versioning)
    service.version_repository = SimpleNamespace(
        get_version=AsyncMock(return_value=version)
    )

    result = await service.restore_version(resume_id, version_id, user_id)

    assert result is resume
    versioning.create_snapshot.assert_awaited_once_with(resume)
    repository.restore_resume.assert_awaited_once_with(
        resume_id=resume_id,
        user_id=user_id,
        command=UpdateResumeCommand(title="Previous"),
        sections=(
            (
                1,
                CreateSectionCommand(
                    section_type=SectionType.SUMMARY,
                    content={"text": "Restored"},
                ),
            ),
        ),
    )
    repository.session.commit.assert_awaited_once_with()
