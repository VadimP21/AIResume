"""Содержит компоненты модуля resume_version."""

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.resume_version import ResumeVersion


class ResumeVersionRepository:
    """Представляет сущность ResumeVersionRepository."""

    def __init__(self, session: AsyncSession):
        """Инициализирует экземпляр."""
        self.session = session

    async def create_version(
        self,
        resume_id: UUID,
        snapshot: dict,
    ) -> ResumeVersion:
        """Создаёт version."""
        version = ResumeVersion(
            resume_id=resume_id,
            snapshot=snapshot,
        )

        self.session.add(version)
        await self.session.flush()

        return version

    async def list_versions(
        self,
        resume_id: UUID,
        limit: int,
        offset: int,
    ) -> list[ResumeVersion]:
        """Выполняет операцию list versions."""
        query = (
            select(ResumeVersion)
            .where(ResumeVersion.resume_id == resume_id)
            .order_by(ResumeVersion.created_at.desc())
            .limit(limit)
            .offset(offset)
        )

        result = await self.session.execute(query)

        return list(result.scalars().all())

    async def get_version(
        self,
        resume_id: UUID,
        version_id: UUID,
    ) -> ResumeVersion | None:
        """Возвращает версию резюме по идентификатору."""
        query = select(ResumeVersion).where(
            ResumeVersion.id == version_id,
            ResumeVersion.resume_id == resume_id,
        )
        result = await self.session.execute(query)
        return result.scalar_one_or_none()
