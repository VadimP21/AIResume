from app.models.resume import Resume
from app.repositories.resume_version import (
    ResumeVersionRepository,
)


class VersioningService:

    def __init__(
            self,
            repository: ResumeVersionRepository,
    ):
        self.repository = repository

    async def create_snapshot(
            self,
            resume: Resume,
    ):
        snapshot = {
            "resume": {
                "id": str(resume.id),
                "title": resume.title,
            },
            "sections": [
                {
                    "id": str(section.id),
                    "type": section.type.value,
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
