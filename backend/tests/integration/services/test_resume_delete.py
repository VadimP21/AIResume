import os
from uuid import uuid4

import pytest
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from app.db.models import Resume, User
from app.repositories.resume import ResumeRepository
from app.services.resume import ResumeService

TEST_DATABASE_URL = os.getenv("TEST_DATABASE_URL")

pytestmark = pytest.mark.skipif(
    not TEST_DATABASE_URL,
    reason="TEST_DATABASE_URL is not configured",
)


@pytest.mark.asyncio
async def test_deleted_resume_is_absent_in_new_session() -> None:
    assert TEST_DATABASE_URL is not None
    engine = create_async_engine(TEST_DATABASE_URL)
    session_factory = async_sessionmaker(engine, expire_on_commit=False)
    user_id = None

    try:
        async with session_factory() as setup_session:
            user = User(
                email=f"resume-delete-{uuid4()}@example.com",
                hashed_password="integration-test-only",
            )
            setup_session.add(user)
            await setup_session.flush()

            resume = Resume(
                user_id=user.id,
                title="Delete integration test",
            )
            setup_session.add(resume)
            await setup_session.commit()
            user_id = user.id
            resume_id = resume.id

        async with session_factory() as delete_session:
            service = ResumeService(ResumeRepository(delete_session))
            await service.delete_resume(resume_id, user_id)

        async with session_factory() as verification_session:
            repository = ResumeRepository(verification_session)
            deleted_resume = await repository.get_resume_base(
                resume_id=resume_id,
                user_id=user_id,
            )

        assert deleted_resume is None
    finally:
        if user_id is not None:
            async with session_factory() as cleanup_session:
                user = await cleanup_session.get(User, user_id)
                if user is not None:
                    await cleanup_session.delete(user)
                    await cleanup_session.commit()
        await engine.dispose()
