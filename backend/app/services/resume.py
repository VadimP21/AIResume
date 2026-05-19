from uuid import UUID

from app.repositories.resume import ResumeRepository
from app.schemas.resume import (
    ResumeCreateSchema,
    ResumeSectionCreateSchema,
)
from app.core.exceptions import NotFoundException


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
        resume = await self.repository.create_resume(
            user_id=user_id,
            title=data.title,
        )

        await self.repository.session.commit()

        return resume

    async def get_resume(
            self,
            resume_id: UUID,
            user_id: UUID,
    ):

        resume = await self.repository.get_resume(
            resume_id,
            user_id,
        )

        if not resume:
            raise NotFoundException(
                "Resume not found"
            )

        return resume

    async def list_resumes(
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

    async def add_section(
            self,
            resume_id: UUID,
            user_id: UUID,
            data: ResumeSectionCreateSchema,
    ):

        resume = await self.repository.get_resume(
            resume_id,
            user_id,
        )

        if not resume:
            raise NotFoundException(
                "Resume not found"
            )

        position = await self.repository.get_next_position(resume_id)

        section = await self.repository.add_section(
            resume_id=resume_id,
            type=data.type,
            content=data.content,
            position=position,
        )

        await self.repository.session.commit()
        return section
