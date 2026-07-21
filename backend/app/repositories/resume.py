"""Содержит компоненты модуля resume."""

from typing import Any
from uuid import UUID

from sqlalchemy import delete, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.dto.common import UnsetType
from app.dto.resumes import (
    CreateResumeCommand,
    CreateSectionCommand,
    ResumeDTO,
    ResumeSectionDTO,
    SectionType,
    UpdateResumeCommand,
    UpdateSectionCommand,
)
from app.models.resume import Resume
from app.models.resume_section import ResumeSection
from app.repositories.mappers.resumes import resume_to_dto


class ResumeRepository:
    """Представляет сущность ResumeRepository."""

    def __init__(self, session: AsyncSession):
        """Инициализирует экземпляр."""
        self.session = session

    async def create_resume(
        self,
        user_id: UUID,
        command: CreateResumeCommand,
    ) -> ResumeDTO:
        """Создаёт резюме и возвращает DTO."""
        resume = await self._create_resume_orm(user_id, command.title)
        return resume_to_dto(resume)

    async def _create_resume_orm(self, user_id: UUID, title: str) -> Resume:
        """Создаёт ORM-резюме для внутренних сценариев."""
        """Создаёт resume."""
        resume = Resume(
            user_id=user_id,
            title=title,
        )

        self.session.add(resume)
        await self.session.flush()

        return resume

    async def _get_resume_base(
        self,
        user_id: UUID,
        resume_id: UUID,
    ) -> Resume | None:
        """Возвращает resume base."""
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
    ) -> ResumeDTO | None:
        """Возвращает DTO резюме с заранее загруженными секциями."""
        resume = await self._get_resume_with_sections_orm(resume_id, user_id)
        return resume_to_dto(resume) if resume is not None else None

    async def _get_resume_with_sections_orm(
        self,
        resume_id: UUID,
        user_id: UUID,
    ) -> Resume | None:
        """Возвращает resume with sections."""
        query = (
            select(Resume)
            .options(selectinload(Resume.sections))
            .where(Resume.id == resume_id, Resume.user_id == user_id)
        )

        result = await self.session.execute(query)

        return result.scalar_one_or_none()

    async def update_resume(
        self,
        resume_id: UUID,
        user_id: UUID,
        command: UpdateResumeCommand,
    ) -> ResumeDTO | None:
        """Обновляет резюме и возвращает DTO."""
        resume = await self._get_resume_with_sections_orm(resume_id, user_id)
        if resume is None:
            return None
        await self._update_resume_orm(resume, command.title)
        return resume_to_dto(resume)

    async def _update_resume_orm(
        self, resume: Resume, title: str | None | UnsetType
    ) -> Resume:
        """Обновляет resume."""
        if isinstance(title, str):
            resume.title = title

        await self.session.flush()

        return resume

    async def list_resumes(
        self,
        user_id: UUID,
        limit: int,
        offset: int,
    ) -> list[ResumeDTO]:
        """Выполняет операцию list resumes."""
        query = (
            select(Resume)
            .where(Resume.user_id == user_id)
            .options(selectinload(Resume.sections))
            .order_by(Resume.created_at.desc())
            .limit(limit)
            .offset(offset)
        )

        result = await self.session.scalars(query)

        return [resume_to_dto(resume) for resume in result.all()]

    async def delete_resume(
        self,
        resume_id: UUID,
        user_id: UUID,
    ) -> bool:
        """Удаляет resume."""
        resume = await self._get_resume_base(user_id, resume_id)
        if resume is None:
            return False
        await self.session.delete(resume)
        return True

    async def _lock_resume(
        self,
        resume_id: UUID,
        user_id: UUID,
    ) -> Resume | None:
        """Выполняет операцию lock resume."""
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
        position: int,
        command: CreateSectionCommand,
    ) -> ResumeSectionDTO:
        """Создаёт секцию и возвращает DTO."""
        section = await self._add_section_orm(
            resume_id, command.section_type, command.content, position
        )
        return ResumeSectionDTO(
            id=section.id,
            resume_id=section.resume_id,
            section_type=section.section_type,
            position=section.position,
            content=section.content,
            created_at=section.created_at,
            updated_at=section.updated_at,
        )

    async def _add_section_orm(
        self,
        resume_id: UUID,
        section_type: SectionType,
        content: dict[str, Any],
        position: int,
    ) -> ResumeSection:
        """Выполняет операцию add section."""
        section = ResumeSection(
            resume_id=resume_id,
            section_type=section_type,
            content=content,
            position=position,
        )

        self.session.add(section)

        return section

    async def _get_section(
        self,
        section_id: UUID,
        user_id: UUID,
    ) -> ResumeSection | None:
        """Возвращает section."""
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
        self, section_id: UUID, user_id: UUID, command: UpdateSectionCommand
    ) -> ResumeSectionDTO | None:
        """Обновляет секцию и возвращает DTO."""
        section = await self._get_section(section_id, user_id)
        if section is None:
            return None
        await self._update_section_orm(section, command.content)
        return ResumeSectionDTO(
            id=section.id,
            resume_id=section.resume_id,
            section_type=section.section_type,
            position=section.position,
            content=section.content,
            created_at=section.created_at,
            updated_at=section.updated_at,
        )

    async def _update_section_orm(
        self, section: ResumeSection, content: dict[str, Any] | None | UnsetType
    ) -> ResumeSection:
        """Обновляет section."""
        if isinstance(content, dict):
            section.content = content

        await self.session.flush()

        return section

    async def _delete_sections(self, resume_id: UUID) -> None:
        """Удаляет все секции резюме."""
        await self.session.execute(
            delete(ResumeSection).where(ResumeSection.resume_id == resume_id)
        )

    async def restore_resume(
        self,
        resume_id: UUID,
        user_id: UUID,
        command: UpdateResumeCommand,
        sections: tuple[tuple[int, CreateSectionCommand], ...],
    ) -> ResumeDTO | None:
        """Восстанавливает резюме и его секции из команд."""
        resume = await self._get_resume_base(user_id, resume_id)
        if resume is None:
            return None
        await self._update_resume_orm(resume, command.title)
        await self._delete_sections(resume_id)
        for position, section in sections:
            await self._add_section_orm(
                resume_id,
                section.section_type,
                section.content,
                position,
            )
        await self.session.flush()
        return await self.get_resume_with_sections(resume_id, user_id)

    async def get_next_position(
        self,
        resume_id: UUID,
    ) -> int:
        """Возвращает next position."""
        query = select(func.max(ResumeSection.position)).where(
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
        """Возвращает next position and lock resume."""
        resume = await self._lock_resume(resume_id, user_id)
        if resume is None:
            return None

        return await self.get_next_position(resume_id)
