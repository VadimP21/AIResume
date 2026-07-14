"""Содержит компоненты модуля router."""

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Query
from starlette import status

from app.api.v1.auth.dependencies import get_current_user
from app.api.v1.resumes.dependencies import (
    get_resume_service,
)
from app.models.user import User
from app.schemas.resume import (
    ResumeCreateSchema,
    ResumeResponseSchema,
    ResumeSectionCreateSchema,
    ResumeSectionResponseSchema,
    ResumeSectionUpdateSchema,
    ResumeUpdateSchema,
)
from app.services.resume import ResumeService

router = APIRouter(
    prefix="/resumes",
    tags=["Resumes"],
)


@router.post(
    "",
    response_model=ResumeResponseSchema,
    status_code=status.HTTP_201_CREATED,
)
async def create_resume(
    data: ResumeCreateSchema,
    service: Annotated[ResumeService, Depends(get_resume_service)],
    current_user: User = Depends(get_current_user),
):
    """Создаёт resume."""
    return await service.create_resume(
        user_id=current_user.id,
        data=data,
    )


@router.get(
    "/{resume_id}",
    response_model=ResumeResponseSchema,
    status_code=status.HTTP_200_OK,
)
async def get_resume(
    resume_id: UUID,
    current_user: User = Depends(get_current_user),
    service: ResumeService = Depends(get_resume_service),
):
    """Возвращает resume."""
    return await service.get_resume(resume_id, current_user.id)


@router.patch(
    "/{resume_id}",
    response_model=ResumeResponseSchema,
)
async def update_resume(
    resume_id: UUID,
    data: ResumeUpdateSchema,
    current_user: User = Depends(get_current_user),
    service: ResumeService = Depends(get_resume_service),
):
    """Обновляет resume."""
    return await service.update_resume(
        resume_id,
        current_user.id,
        data,
    )


@router.delete(
    "/{resume_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_resume(
    resume_id: UUID,
    current_user: User = Depends(get_current_user),
    service: ResumeService = Depends(get_resume_service),
):
    """Удаляет resume."""
    await service.delete_resume(resume_id, current_user.id)


@router.post(
    "/{resume_id}/sections",
    response_model=ResumeSectionResponseSchema,
    status_code=status.HTTP_201_CREATED,
)
async def add_section(
    resume_id: UUID,
    data: ResumeSectionCreateSchema,
    current_user: User = Depends(get_current_user),
    service: ResumeService = Depends(get_resume_service),
):
    """Выполняет операцию add section."""
    return await service.add_section(
        resume_id=resume_id,
        user_id=current_user.id,
        data=data,
    )


@router.patch(
    "/sections/{section_id}",
    response_model=ResumeSectionResponseSchema,
)
async def update_section(
    section_id: UUID,
    data: ResumeSectionUpdateSchema,
    current_user: User = Depends(get_current_user),
    service: ResumeService = Depends(get_resume_service),
):
    """Обновляет section."""
    return await service.update_section(
        section_id,
        current_user.id,
        data,
    )


@router.get(
    "/",
    response_model=list[ResumeResponseSchema],
    status_code=status.HTTP_200_OK,
)
async def list_resumes(
    current_user: User = Depends(get_current_user),
    service: ResumeService = Depends(get_resume_service),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
):
    """Выполняет операцию list resumes."""
    return await service.get_list_resumes(current_user.id, limit, offset)
