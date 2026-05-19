from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.repositories.resume import ResumeRepository
from app.services.resume import ResumeService

def get_resume_repository(
        session: AsyncSession = Depends(get_db),
):
    return ResumeRepository(session)

def get_resume_service(
    session: AsyncSession = Depends(get_db),
):
    repository = ResumeRepository(session)
    return ResumeService(repository)