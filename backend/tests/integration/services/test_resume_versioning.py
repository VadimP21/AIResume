"""Содержит компоненты модуля test_resume_versioning."""

from uuid import uuid4

import pytest
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.models.resume import Resume
from app.models.resume_section import ResumeSection, SectionType
from app.models.user import User
from app.repositories.resume_version import ResumeVersionRepository
from app.services.versioning import VersioningService


@pytest.mark.asyncio
async def test_resume_version_is_persisted_and_read(
    test_session_factory: async_sessionmaker[AsyncSession],
) -> None:
    """Проверяет сценарий resume version is persisted and read."""
    async with test_session_factory() as session:
        user = User(
            email=f"version-{uuid4()}@example.com",
            hashed_password="integration-test-only",
        )
        session.add(user)
        await session.flush()
        resume = Resume(user_id=user.id, title="Version integration test")
        session.add(resume)
        await session.flush()
        section = ResumeSection(
            resume_id=resume.id,
            section_type=SectionType.SUMMARY,
            position=1,
            content={"text": "Summary"},
        )
        session.add(section)
        await session.commit()

        await session.refresh(resume, attribute_names=["sections"])
        repository = ResumeVersionRepository(session)
        version = await VersioningService(repository).create_snapshot(resume)
        versions = await repository.list_versions(resume.id)

        assert versions == [version]
        assert version.snapshot["sections"][0]["type"] == "summary"

        await session.delete(user)
        await session.commit()
