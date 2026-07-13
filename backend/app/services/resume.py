from uuid import UUID

from app.core.exceptions import NotFoundException
from app.repositories.resume import ResumeRepository
from app.schemas.resume import (
    ResumeCreateSchema,
    ResumeSectionCreateSchema,
    ResumeSectionUpdateSchema,
    ResumeUpdateSchema,
)


class ResumeService:
    def __init__(
        self,
        repository: ResumeRepository,
    ):
        self.repository = repository

    async def create_resume(
        self,
        user_id: UUID,
        data: ResumeCreateSchema,
    ):
        try:
            resume = await self.repository.create_resume(
                user_id=user_id,
                title=data.title,
            )
            resume_id = resume.id

            await self.repository.session.commit()
            return await self.repository.get_resume_with_sections(
                user_id=user_id, resume_id=resume_id
            )

        except Exception:
            await self.repository.session.rollback()
            raise

    async def get_resume(
        self,
        resume_id: UUID,
        user_id: UUID,
    ):

        resume = await self.repository.get_resume_with_sections(
            user_id=user_id,
            resume_id=resume_id,
        )

        if not resume:
            raise NotFoundException("Resume not found")

        return resume

    async def update_resume(
        self,
        resume_id: UUID,
        user_id: UUID,
        data: ResumeUpdateSchema,
    ):

        resume = await self.repository.get_resume_base(
            resume_id,
            user_id,
        )

        if not resume:
            raise NotFoundException("Resume not found")
        try:
            resume = await self.repository.update_resume(
                resume=resume,
                title=data.title,
            )

            await self.repository.session.commit()
            await self.repository.session.refresh(resume)

            return resume

        except Exception:
            await self.repository.session.rollback()
            raise

    async def get_list_resumes(
        self,
        user_id: UUID,
        limit: int,
        offset: int,
    ):

        return await self.repository.list_resumes(
            user_id,
            limit,
            offset,
        )

    async def delete_resume(
        self,
        resume_id: UUID,
        user_id: UUID,
    ):
        resume = await self.repository.get_resume_base(
            resume_id=resume_id,
            user_id=user_id,
        )
        if not resume:
            raise NotFoundException("Resume not found")

        try:
            await self.repository.session.delete(resume)
            await self.repository.session.flush()
            await self.repository.session.commit()
        except Exception:
            await self.repository.session.rollback()
            raise

    async def add_section(
        self,
        resume_id: UUID,
        user_id: UUID,
        data: ResumeSectionCreateSchema,
    ):
        try:
            position = await self.repository.get_next_position_and_lock_resume(
                resume_id,
                user_id,
            )

            if not position:
                raise NotFoundException("Resume not found")

            section = await self.repository.add_section(
                resume_id=resume_id,
                section_type=data.section.section_type,
                content=data.section.content,
                position=position,
            )

            await self.repository.session.commit()
            await self.repository.session.refresh(section)
            return section

        except Exception:
            await self.repository.session.rollback()
            raise

    async def update_section(
        self,
        section_id: UUID,
        user_id: UUID,
        data: ResumeSectionUpdateSchema,
    ):

        section = await self.repository.get_section(
            section_id,
            user_id,
        )

        if not section:
            raise NotFoundException("Section not found")
        try:
            section = await self.repository.update_section(
                section,
                data.content,
            )

            await self.repository.session.commit()
            await self.repository.session.refresh(section)

            return section

        except Exception:
            await self.repository.session.rollback()
            raise
