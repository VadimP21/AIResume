import asyncio
from uuid import uuid4

import pytest
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.models.resume import Resume
from app.models.resume_section import SectionType
from app.models.user import User
from app.repositories.resume import ResumeRepository
from app.schemas.resume import ResumeSectionCreateSchema
from app.schemas.section import SummaryContent, SummarySection
from app.services.resume import ResumeService


def section_data() -> ResumeSectionCreateSchema:
    return ResumeSectionCreateSchema(
        section=SummarySection(
            section_type=SectionType.SUMMARY,
            content=SummaryContent(text="Summary"),
        ),
    )


async def create_resume(session_factory: async_sessionmaker[AsyncSession]) -> tuple:
    async with session_factory() as session:
        user = User(
            email=f"sections-{uuid4()}@example.com",
            hashed_password="integration-test-only",
        )
        session.add(user)
        await session.flush()
        resume = Resume(user_id=user.id, title="Sections integration test")
        session.add(resume)
        await session.commit()
        return user.id, resume.id


@pytest.mark.asyncio
async def test_sections_receive_sequential_positions(
    test_session_factory: async_sessionmaker[AsyncSession],
) -> None:
    user_id, resume_id = await create_resume(test_session_factory)
    try:
        async with test_session_factory() as session:
            service = ResumeService(ResumeRepository(session))
            first = await service.add_section(resume_id, user_id, section_data())
            second = await service.add_section(resume_id, user_id, section_data())

        assert (first.position, second.position) == (1, 2)
    finally:
        async with test_session_factory() as session:
            user = await session.get(User, user_id)
            if user is not None:
                await session.delete(user)
                await session.commit()


@pytest.mark.asyncio
async def test_parallel_section_creation_assigns_unique_positions(
    test_session_factory: async_sessionmaker[AsyncSession],
) -> None:
    user_id, resume_id = await create_resume(test_session_factory)
    try:

        async def add_section() -> int:
            async with test_session_factory() as session:
                section = await ResumeService(ResumeRepository(session)).add_section(
                    resume_id,
                    user_id,
                    section_data(),
                )
                return section.position

        positions = await asyncio.gather(add_section(), add_section())
        assert sorted(positions) == [1, 2]
    finally:
        async with test_session_factory() as session:
            user = await session.get(User, user_id)
            if user is not None:
                await session.delete(user)
                await session.commit()
