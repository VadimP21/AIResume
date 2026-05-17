from uuid import UUID

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.resume import Resume
from app.models.resume_section import ResumeSection


class ResumeRepository:

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_resume(
            self,
            user_id: UUID,
            title: str,
    ) -> Resume:
        resume = Resume(
            user_id=user_id,
            title=title,
        )

        self.session.add(resume)
        await self.session.flush()

        return resume

    async def get_resume(
            self,
            resume_id: UUID,
            user_id: UUID,
    ) -> Resume | None:
        query = (
            select(Resume)
            .options(
                selectinload(Resume.sections)
            )
            .where(Resume.id == resume_id)
            .where(Resume.user_id == user_id)
        )

        result = await self.session.execute(query)

        return result.scalar_one_or_none()

    async def list_resumes(
            self,
            user_id: UUID,
            limit: int,
            offset: int,
    ) -> list[Resume]:
        query = (
            select(Resume)
            .options(
                selectinload(Resume.sections)
            )
            .where(Resume.user_id == user_id)
            .limit(limit)
            .offset(offset)
        )

        result = await self.session.execute(query)

        return list(result.scalars().all())

    async def delete_resume(
            self,
            resume: Resume,
    ) -> None:
        await self.session.delete(resume)
        await self.session.commit()

    async def add_section(
            self,
            resume_id: UUID,
            type,
            content: dict,
            position: int,
    ) -> ResumeSection:
        section = ResumeSection(
            resume_id=resume_id,
            type=type,
            content=content,
            position=position,
        )

        self.session.add(section)
        await self.session.flush()

        return section

    async def get_next_position(
            self,
            resume_id: UUID,
    ) -> int:
        query = select(
            func.max(ResumeSection.position)
        ).where(
            ResumeSection.resume_id == resume_id
        )

        result = await self.session.execute(query)

        max_position = result.scalar()

        return (max_position or 0) + 1
