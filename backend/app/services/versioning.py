"""Содержит компоненты модуля versioning."""

from app.models.resume import Resume
from app.models.resume_version import ResumeVersion
from app.repositories.resume_version import (
    ResumeVersionRepository,
)


class VersioningService:
    """Представляет сущность VersioningService."""

    def __init__(
        self,
        repository: ResumeVersionRepository,
    ):
        """Инициализирует экземпляр."""
        self.repository = repository

    async def create_snapshot(
        self,
        resume: Resume,
    ) -> ResumeVersion:
        """Создаёт snapshot."""
        snapshot = {
            "resume": {
                "id": str(resume.id),
                "title": resume.title,
            },
            "sections": [
                {
                    "id": str(section.id),
                    "type": section.section_type.value,
                    "position": section.position,
                    "content": section.content,
                }
                for section in resume.sections
            ],
        }

        return await self.repository.create_version(
            resume_id=resume.id,
            snapshot=snapshot,
        )
