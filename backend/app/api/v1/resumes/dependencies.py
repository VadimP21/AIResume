"""Содержит компоненты модуля dependencies."""

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.repositories.resume import ResumeRepository
from app.services.resume import ResumeService


def get_resume_service(
    session: AsyncSession = Depends(get_db),
):
    """Возвращает resume service."""
    repo = ResumeRepository(session)
    return ResumeService(repository=repo)
