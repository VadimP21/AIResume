"""Содержит компоненты модуля resume."""

import asyncio
import re
from typing import TYPE_CHECKING
from uuid import UUID

from app.core.exceptions import (
    NotFoundException,
    ServiceUnavailableException,
    ValidationException,
)
from app.models.resume import Resume
from app.models.resume_section import ResumeSection, SectionType
from app.models.resume_version import ResumeVersion
from app.repositories.resume import ResumeRepository
from app.repositories.resume_version import ResumeVersionRepository
from app.schemas.resume import (
    ResumeCreateSchema,
    ResumeSectionCreateSchema,
    ResumeSectionUpdateSchema,
    ResumeUpdateSchema,
)
from app.schemas.resume_import import ImportedResumeSchema
from app.services.resume_ai_parser import RESUME_IMPORT_UNAVAILABLE_MESSAGE

if TYPE_CHECKING:
    from app.services.resume_ai_parser import ResumeAIParser
    from app.services.resume_document import ResumeDocumentRenderer
    from app.services.resume_file import ResumeFileExtractor
    from app.services.versioning import VersioningService


class ResumeService:
    """Представляет сущность ResumeService."""

    def __init__(
        self,
        repository: ResumeRepository,
        extractor: "ResumeFileExtractor | None" = None,
        parser: "ResumeAIParser | None" = None,
        renderer: "ResumeDocumentRenderer | None" = None,
        versioning: "VersioningService | None" = None,
    ) -> None:
        """Инициализирует экземпляр."""
        self.repository = repository
        self.extractor = extractor
        self.parser = parser
        self.renderer = renderer
        self.versioning = versioning
        self.version_repository = ResumeVersionRepository(repository.session)

    async def create_resume(
        self,
        user_id: UUID,
        data: ResumeCreateSchema,
    ) -> Resume | None:
        """Создаёт resume."""
        try:
            resume = await self.repository.create_resume(
                user_id=user_id,
                title=data.title,
            )
            resume_id = resume.id
            await self._create_snapshot(resume)
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
    ) -> Resume:
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
    ) -> Resume:
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
            await self._create_snapshot_by_id(resume_id, user_id)
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
    ) -> list[Resume]:
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
    ) -> Resume | None:
        """Создаёт черновик резюме из импортированного файла."""
        if self.extractor is None:
            raise ValidationException("Resume import is not configured")
        if self.parser is None:
            raise ServiceUnavailableException(RESUME_IMPORT_UNAVAILABLE_MESSAGE)
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
    ) -> Resume | None:
        """Сохраняет структурированное импортированное резюме."""
        resume = await self.repository.create_resume(user_id, imported.title)
        for position, section in enumerate(imported.sections):
            await self.repository.add_section(
                resume_id=resume.id,
                section_type=section.section_type,
                content=section.content.model_dump(mode="json"),
                position=position,
            )
        await self._create_snapshot_by_id(resume.id, user_id)
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
    ) -> None:
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
    ) -> ResumeSection:
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
            await self._create_snapshot_by_id(resume_id, user_id)
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
    ) -> ResumeSection:
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
            await self._create_snapshot_by_id(section.resume_id, user_id)
            await self.repository.session.commit()
            await self.repository.session.refresh(section)

            return section

        except Exception:
            await self.repository.session.rollback()
            raise

    async def list_versions(
        self,
        resume_id: UUID,
        user_id: UUID,
        limit: int,
        offset: int,
    ) -> list[ResumeVersion]:
        """Возвращает историю версий резюме владельца."""
        await self._get_resume_for_snapshot(resume_id, user_id)
        return await self.version_repository.list_versions(resume_id, limit, offset)

    async def get_version(
        self,
        resume_id: UUID,
        version_id: UUID,
        user_id: UUID,
    ) -> ResumeVersion:
        """Возвращает версию резюме владельца."""
        await self._get_resume_for_snapshot(resume_id, user_id)
        version = await self.version_repository.get_version(resume_id, version_id)
        if version is None:
            raise NotFoundException("Resume version not found")
        return version

    async def restore_version(
        self,
        resume_id: UUID,
        version_id: UUID,
        user_id: UUID,
    ) -> Resume:
        """Восстанавливает резюме из сохранённой версии."""
        resume = await self._get_resume_for_snapshot(resume_id, user_id)
        version = await self.version_repository.get_version(resume_id, version_id)
        if version is None:
            raise NotFoundException("Resume version not found")

        try:
            await self._create_snapshot(resume)
            snapshot_resume = version.snapshot["resume"]
            await self.repository.update_resume(resume, snapshot_resume["title"])
            await self.repository.delete_sections(resume.id)
            for section in version.snapshot["sections"]:
                await self.repository.add_section(
                    resume_id=resume.id,
                    section_type=SectionType(section["type"]),
                    content=section["content"],
                    position=section["position"],
                )
            await self.repository.session.commit()
            return await self._get_resume_for_snapshot(resume_id, user_id)
        except Exception:
            await self.repository.session.rollback()
            raise

    async def _get_resume_for_snapshot(
        self,
        resume_id: UUID,
        user_id: UUID,
    ) -> Resume:
        """Возвращает резюме владельца с загруженными секциями."""
        resume = await self.repository.get_resume_with_sections(resume_id, user_id)
        if resume is None:
            raise NotFoundException("Resume not found")
        return resume

    async def _create_snapshot(self, resume: Resume) -> None:
        """Создаёт снимок резюме при включённом версионировании."""
        if self.versioning is not None:
            await self.versioning.create_snapshot(resume)

    async def _create_snapshot_by_id(self, resume_id: UUID, user_id: UUID) -> None:
        """Создаёт снимок резюме с секциями при включённом версионировании."""
        if self.versioning is None:
            return
        resume = await self._get_resume_for_snapshot(resume_id, user_id)
        await self.versioning.create_snapshot(resume)
