"""Содержит компоненты модуля resume."""

import asyncio
import re
from typing import TYPE_CHECKING
from uuid import UUID

from app.core.exceptions import NotFoundException, ValidationException
from app.repositories.resume import ResumeRepository
from app.schemas.resume import (
    ResumeCreateSchema,
    ResumeSectionCreateSchema,
    ResumeSectionUpdateSchema,
    ResumeUpdateSchema,
)
from app.schemas.resume_import import ImportedResumeSchema

if TYPE_CHECKING:
    from app.services.resume_ai_parser import ResumeAIParser
    from app.services.resume_document import ResumeDocumentRenderer
    from app.services.resume_file import ResumeFileExtractor


class ResumeService:
    """Представляет сущность ResumeService."""

    def __init__(
        self,
        repository: ResumeRepository,
        extractor: "ResumeFileExtractor | None" = None,
        parser: "ResumeAIParser | None" = None,
        renderer: "ResumeDocumentRenderer | None" = None,
    ):
        """Инициализирует экземпляр."""
        self.repository = repository
        self.extractor = extractor
        self.parser = parser
        self.renderer = renderer

    async def create_resume(
        self,
        user_id: UUID,
        data: ResumeCreateSchema,
    ):
        """Создаёт resume."""
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
        """Возвращает resume."""
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
        """Обновляет resume."""
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
        """Возвращает list resumes."""
        return await self.repository.list_resumes(
            user_id,
            limit,
            offset,
        )

    async def import_resume(
        self,
        user_id: UUID,
        filename: str,
        content: bytes,
    ):
        """Создаёт черновик резюме из импортированного файла."""
        if self.extractor is None or self.parser is None:
            raise ValidationException("Resume import is not configured")
        try:
            text = await asyncio.to_thread(self.extractor.extract, filename, content)
            imported = await self.parser.parse(text)
            return await self._save_imported_resume(user_id, imported)
        except Exception:
            await self.repository.session.rollback()
            raise

    async def _save_imported_resume(
        self,
        user_id: UUID,
        imported: ImportedResumeSchema,
    ):
        """Сохраняет структурированное импортированное резюме."""
        resume = await self.repository.create_resume(user_id, imported.title)
        for position, section in enumerate(imported.sections):
            await self.repository.add_section(
                resume_id=resume.id,
                section_type=section.section_type,
                content=section.content.model_dump(mode="json"),
                position=position,
            )
        await self.repository.session.commit()
        return await self.repository.get_resume_with_sections(user_id, resume.id)

    async def export_resume(
        self,
        resume_id: UUID,
        user_id: UUID,
        export_format: str,
    ) -> tuple[bytes, str]:
        """Экспортирует резюме владельца без изменений в БД."""
        if self.renderer is None:
            from app.services.resume_document import ResumeDocumentRenderer

            self.renderer = ResumeDocumentRenderer()
        resume = await self.get_resume(resume_id, user_id)
        if export_format == "pdf":
            content = self.renderer.render_pdf(resume)
        elif export_format == "docx":
            content = self.renderer.render_docx(resume)
        else:
            raise ValidationException("Unsupported export format")
        filename = self._export_filename(resume.title, export_format)
        return content, filename

    @staticmethod
    def _export_filename(title: str, export_format: str) -> str:
        """Возвращает безопасное имя экспортируемого файла."""
        safe_title = re.sub(r"[^A-Za-z0-9_-]+", "_", title).strip("_")
        return f"{safe_title or 'resume'}.{export_format}"

    async def delete_resume(
        self,
        resume_id: UUID,
        user_id: UUID,
    ):
        """Удаляет resume."""
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
        """Выполняет операцию add section."""
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
                content=data.section.content.model_dump(mode="json"),
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
        """Обновляет section."""
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
