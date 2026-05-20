from types import SimpleNamespace
from unittest.mock import AsyncMock
from uuid import uuid4

import pytest

from app.services.resume import ResumeService


def make_repository(resume: object) -> SimpleNamespace:
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
    resume = object()
    repository = make_repository(resume)
    repository.session.commit.side_effect = RuntimeError("commit failed")
    service = ResumeService(repository)

    with pytest.raises(RuntimeError, match="commit failed"):
        await service.delete_resume(uuid4(), uuid4())

    repository.session.rollback.assert_awaited_once_with()
