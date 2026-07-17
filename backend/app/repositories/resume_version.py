"""Содержит компоненты модуля resume_version."""

from typing import Any
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.dto.versions import ResumeVersionDTO
from app.models.resume_version import ResumeVersion
from app.repositories.mappers.versions import version_to_dto


class ResumeVersionRepository:
    """Представляет сущность ResumeVersionRepository."""

    def __init__(self, session: AsyncSession):
        """Инициализирует экземпляр."""
        self.session = session

    async def create_version(
        self,
        resume_id: UUID,
        snapshot: dict[str, Any],
    ) -> ResumeVersionDTO:
        """Создаёт version."""
        version = ResumeVersion(
            resume_id=resume_id,
            snapshot=snapshot,
        )

        self.session.add(version)
        await self.session.flush()

        return version_to_dto(version)

    async def list_versions(
        self,
        resume_id: UUID,
        limit: int,
        offset: int,
    ) -> list[ResumeVersionDTO]:
        """Выполняет операцию list versions."""
        query = (
            select(ResumeVersion)
            .where(ResumeVersion.resume_id == resume_id)
            .order_by(ResumeVersion.created_at.desc())
            .limit(limit)
            .offset(offset)
        )

        result = await self.session.execute(query)

        return [version_to_dto(version) for version in result.scalars().all()]

    async def get_version(
        self,
        resume_id: UUID,
        version_id: UUID,
    ) -> ResumeVersionDTO | None:
        """Возвращает версию резюме по идентификатору."""
        query = select(ResumeVersion).where(
            ResumeVersion.id == version_id,
            ResumeVersion.resume_id == resume_id,
        )
        result = await self.session.execute(query)
        version = result.scalar_one_or_none()
        return version_to_dto(version) if version is not None else None
