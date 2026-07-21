"""Содержит компоненты модуля resume."""

import asyncio
import re
from typing import TYPE_CHECKING, Any, cast
from uuid import UUID

from app.core.exceptions import (
    NotFoundException,
    ServiceUnavailableException,
    ValidationException,
)
from app.dto.resumes import (
    CreateResumeCommand,
    CreateSectionCommand,
    ResumeDTO,
    ResumeSectionDTO,
    SectionType,
    UpdateResumeCommand,
    UpdateSectionCommand,
)
from app.dto.versions import ResumeVersionDTO
from app.repositories.resume import ResumeRepository
from app.repositories.resume_version import ResumeVersionRepository
from app.schemas.resume import (
    ResumeCreateSchema,
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
    ) -> ResumeDTO | None:
        """Создаёт resume."""
        try:
            resume = await self.repository.create_resume(
                user_id=user_id,
                command=CreateResumeCommand(title=data.title),
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
    ) -> ResumeDTO:
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
        command: UpdateResumeCommand,
    ) -> ResumeDTO:
        """Обновляет resume."""
        resume = await self.repository.update_resume(resume_id, user_id, command)
        if resume is None:
            raise NotFoundException("Resume not found")
        try:
            await self._create_snapshot_by_id(resume_id, user_id)
            await self.repository.session.commit()
            updated_resume = await self.repository.get_resume_with_sections(
                resume_id, user_id
            )
            if updated_resume is None:
                raise NotFoundException("Resume not found")
            return updated_resume

        except Exception:
            await self.repository.session.rollback()
            raise

    async def get_list_resumes(
        self,
        user_id: UUID,
        limit: int,
        offset: int,
    ) -> list[ResumeDTO]:
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
    ) -> ResumeDTO | None:
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
    ) -> ResumeDTO | None:
        """Сохраняет структурированное импортированное резюме."""
        resume = await self.repository.create_resume(
            user_id=user_id,
            command=CreateResumeCommand(title=imported.title),
        )
        for position, section in enumerate(imported.sections):
            await self.repository.add_section(
                resume_id=resume.id,
                position=position,
                command=CreateSectionCommand(
                    section_type=section.section_type,
                    content=section.content.model_dump(mode="json"),
                ),
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
        try:
            deleted = await self.repository.delete_resume(resume_id, user_id)
            if not deleted:
                raise NotFoundException("Resume not found")
            await self.repository.session.flush()
            await self.repository.session.commit()
        except Exception:
            await self.repository.session.rollback()
            raise

    async def add_section(
        self,
        resume_id: UUID,
        user_id: UUID,
        command: CreateSectionCommand,
    ) -> ResumeSectionDTO:
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
                position=position,
                command=command,
            )
            await self._create_snapshot_by_id(resume_id, user_id)
            await self.repository.session.commit()
            return section

        except Exception:
            await self.repository.session.rollback()
            raise

    async def update_section(
        self,
        section_id: UUID,
        user_id: UUID,
        command: UpdateSectionCommand,
    ) -> ResumeSectionDTO:
        """Обновляет section."""
        section = await self.repository.update_section(
            section_id,
            user_id,
            command,
        )
        if section is None:
            raise NotFoundException("Section not found")
        try:
            await self._create_snapshot_by_id(section.resume_id, user_id)
            await self.repository.session.commit()
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
    ) -> list[ResumeVersionDTO]:
        """Возвращает историю версий резюме владельца."""
        await self._get_resume_for_snapshot(resume_id, user_id)
        return await self.version_repository.list_versions(resume_id, limit, offset)

    async def get_version(
        self,
        resume_id: UUID,
        version_id: UUID,
        user_id: UUID,
    ) -> ResumeVersionDTO:
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
    ) -> ResumeDTO:
        """Восстанавливает резюме из сохранённой версии."""
        resume = await self.get_resume(resume_id, user_id)
        version = await self.version_repository.get_version(resume_id, version_id)
        if version is None:
            raise NotFoundException("Resume version not found")

        try:
            await self._create_snapshot(resume)
            snapshot = cast(dict[str, Any], version.snapshot)
            snapshot_resume = cast(dict[str, Any], snapshot["resume"])
            restored_resume = await self.repository.restore_resume(
                resume_id=resume.id,
                user_id=user_id,
                command=UpdateResumeCommand(title=snapshot_resume["title"]),
                sections=tuple(
                    (
                        section["position"],
                        CreateSectionCommand(
                            section_type=SectionType(section["type"]),
                            content=section["content"],
                        ),
                    )
                    for section in cast(list[dict[str, Any]], snapshot["sections"])
                ),
            )
            if restored_resume is None:
                raise NotFoundException("Resume not found")
            await self.repository.session.commit()
            return restored_resume
        except Exception:
            await self.repository.session.rollback()
            raise

    async def _get_resume_for_snapshot(
        self,
        resume_id: UUID,
        user_id: UUID,
    ) -> ResumeDTO:
        """Возвращает резюме владельца с загруженными секциями."""
        return await self.get_resume(resume_id, user_id)

    async def _create_snapshot(self, resume: ResumeDTO) -> None:
        """Создаёт снимок резюме при включённом версионировании."""
        if self.versioning is not None:
            await self.versioning.create_snapshot(resume)

    async def _create_snapshot_by_id(self, resume_id: UUID, user_id: UUID) -> None:
        """Создаёт снимок резюме с секциями при включённом версионировании."""
        if self.versioning is None:
            return
        resume = await self._get_resume_for_snapshot(resume_id, user_id)
        await self.versioning.create_snapshot(resume)
