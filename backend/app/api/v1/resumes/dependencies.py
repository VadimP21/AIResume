"""Содержит компоненты модуля dependencies."""

from fastapi import Depends
from openai import AsyncOpenAI
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.db.session import get_db
from app.repositories.resume import ResumeRepository
from app.repositories.resume_version import ResumeVersionRepository
from app.services.resume import ResumeService
from app.services.resume_ai_parser import ResumeAIParser
from app.services.resume_file import ResumeFileExtractor
from app.services.versioning import VersioningService


def get_resume_service(
    session: AsyncSession = Depends(get_db),
) -> ResumeService:
    """Возвращает resume service."""
    repo = ResumeRepository(session)
    versioning = VersioningService(ResumeVersionRepository(session))
    extractor = ResumeFileExtractor(settings.RESUME_IMPORT_MAX_FILE_SIZE)
    parser = None
    if settings.OPENAI_API_KEY is not None and settings.OPENAI_MODEL is not None:
        parser = ResumeAIParser(
            client=AsyncOpenAI(api_key=settings.OPENAI_API_KEY.get_secret_value()),
            model=settings.OPENAI_MODEL,
        )
    return ResumeService(
        repository=repo,
        extractor=extractor,
        parser=parser,
        versioning=versioning,
    )
