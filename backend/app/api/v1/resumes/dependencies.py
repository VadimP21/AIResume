"""Содержит компоненты модуля dependencies."""

from functools import lru_cache

import structlog
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.db.session import get_db
from app.repositories.resume import ResumeRepository
from app.repositories.resume_version import ResumeVersionRepository
from app.services.ai.exceptions import AIConfigurationError
from app.services.ai.factory import create_ai_client
from app.services.ai.protocols import ResumeAIClient
from app.services.resume import ResumeService
from app.services.resume_ai_parser import ResumeAIParser
from app.services.resume_file import ResumeFileExtractor
from app.services.versioning import VersioningService

logger = structlog.get_logger()


@lru_cache
def get_resume_ai_client() -> ResumeAIClient:
    """Возвращает процессный клиент активного AI-провайдера."""
    return create_ai_client(settings)


def get_resume_ai_parser() -> ResumeAIParser:
    """Возвращает AI-парсер выбранного провайдера."""
    return ResumeAIParser(client=get_resume_ai_client())


def get_resume_service(
    session: AsyncSession = Depends(get_db),
) -> ResumeService:
    """Возвращает resume service."""
    repo = ResumeRepository(session)
    versioning = VersioningService(ResumeVersionRepository(session))
    extractor = ResumeFileExtractor(settings.RESUME_IMPORT_MAX_FILE_SIZE)
    try:
        parser = get_resume_ai_parser()
    except AIConfigurationError:
        logger.warning(
            "resume_ai_configuration_missing",
            provider=settings.AI_PROVIDER,
            error_category="configuration",
        )
        parser = None
    return ResumeService(
        repository=repo,
        extractor=extractor,
        parser=parser,
        versioning=versioning,
    )
