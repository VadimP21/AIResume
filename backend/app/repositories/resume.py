from typing import Any
from uuid import UUID

from sqlalchemy import select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.resume import Resume
from app.models.resume_section import ResumeSection, SectionType
from app.schemas.section import SectionContent


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

    async def get_resume_base(
            self,
            user_id: UUID,
            resume_id: UUID,
    ):
        query = (
            select(Resume)
            .where(Resume.id == resume_id)
            .where(Resume.user_id == user_id)
        )
        result = await self.session.execute(query)

        return result.scalar_one_or_none()

    async def get_resume_with_sections(
            self,
            resume_id: UUID,
            user_id: UUID,
    ) -> Resume | None:
        query = (
            select(Resume)
            .options(
                selectinload(Resume.sections)
            )
            .where(Resume.id == resume_id, Resume.user_id == user_id)
        )

        result = await self.session.execute(query)

        return result.scalar_one_or_none()

    async def update_resume(
            self,
            resume: Resume,
            title: str,
    ) -> Resume:
        if title is not None:
            resume.title = title

        await self.session.flush()

        return resume

    async def list_resumes(
            self,
            user_id: UUID,
            limit: int,
            offset: int,
    ) -> list[Resume]:
        query = (
            select(Resume)
            .where(Resume.user_id == user_id)
            .options(
                selectinload(Resume.sections)
            )
            .order_by(Resume.created_at.desc())
            .limit(limit)
            .offset(offset)
        )

        result = await self.session.scalars(query)

        return result.all()

    async def delete_resume(
            self,
            resume_id: UUID,
            user_id: UUID,
    ) -> None:
        resume = Resume(
            resume_id=resume_id,
            user_id=user_id,
        )
        await self.session.delete(resume)

    async def lock_resume(
            self,
            resume_id: UUID,
            user_id: UUID,
    ) -> Resume | None:
        query = (
            select(Resume)
            .where(
                Resume.id == resume_id,
                Resume.user_id == user_id,
            )
            .with_for_update()
        )

        result = await self.session.execute(query)

        return result.scalar_one_or_none()

    async def add_section(
            self,
            resume_id: UUID,
            section_type: SectionType,
            content: SectionContent.content,
            position: int,
    ) -> ResumeSection:
        section = ResumeSection(
            resume_id=resume_id,
            section_type=section_type,
            content=content,
            position=position,
        )

        self.session.add(section)

        return section

    async def get_section(
            self,
            section_id: UUID,
            user_id: UUID,
    ) -> ResumeSection | None:
        query = (
            select(ResumeSection)
            .join(Resume)
            .where(
                ResumeSection.id == section_id,
                Resume.user_id == user_id,
            )
        )

        result = await self.session.execute(query)

        return result.scalar_one_or_none()

    async def update_section(
            self,
            section: ResumeSection,
            content: dict[str, Any]
    ) -> ResumeSection:
        if content is not None:
            section.content = content

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

    async def get_next_position_and_lock_resume(
            self,
            resume_id: UUID,
            user_id: UUID,
    ) -> int | None:
        query = (
            select(
                func.max(Resume.sections.position)
            ).where(
                Resume.id == resume_id,
                Resume.user_id == user_id,
            )
            .with_for_update()
        )

        result = await self.session.execute(query)

        max_position = result.scalar_one_or_none()

        if max_position is not None:
            return max_position + 1

        return max_position
