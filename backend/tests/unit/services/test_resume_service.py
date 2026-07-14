"""Содержит компоненты модуля test_resume_service."""

from types import SimpleNamespace
from unittest.mock import AsyncMock
from uuid import uuid4

import pytest

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
        get_resume_base=AsyncMock(return_value=resume),
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

    repository.get_resume_base.assert_awaited_once_with(
        resume_id=resume_id,
        user_id=user_id,
    )
    repository.session.delete.assert_awaited_once_with(resume)
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
    resume = SimpleNamespace(id=uuid4(), sections=[])
    repository = SimpleNamespace(
        create_resume=AsyncMock(return_value=resume),
        get_resume_with_sections=AsyncMock(return_value=resume),
        session=SimpleNamespace(commit=AsyncMock(), rollback=AsyncMock()),
    )
    versioning = SimpleNamespace(create_snapshot=AsyncMock())
    service = ResumeService(repository, versioning=versioning)

    await service.create_resume(uuid4(), SimpleNamespace(title="Resume"))

    versioning.create_snapshot.assert_awaited_once_with(resume)
    repository.session.commit.assert_awaited_once_with()


@pytest.mark.asyncio
async def test_restore_version_saves_current_state_before_replacing_sections() -> None:
    """Проверяет сохранение текущего состояния перед восстановлением."""
    resume_id = uuid4()
    version_id = uuid4()
    user_id = uuid4()
    resume = SimpleNamespace(id=resume_id, title="Current", sections=[])
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
        update_resume=AsyncMock(),
        delete_sections=AsyncMock(),
        add_section=AsyncMock(),
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
    repository.delete_sections.assert_awaited_once_with(resume_id)
    repository.add_section.assert_awaited_once()
    repository.session.commit.assert_awaited_once_with()
