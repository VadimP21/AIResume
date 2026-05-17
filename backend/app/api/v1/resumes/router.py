from uuid import UUID

from fastapi import APIRouter, Depends
from starlette import status

from app.api.v1.auth.dependencies import get_current_user
from app.models.user import User
from app.schemas.resume import (
    ResumeCreateSchema,
    ResumeResponseSchema,
    ResumeSectionCreateSchema,
)
from app.services.resume import ResumeService
from app.api.v1.resumes.dependencies import (
    get_resume_service,
)

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
    current_user: User = Depends(get_current_user),
    service: ResumeService = Depends(
        get_resume_service
    ),
):

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
    service: ResumeService = Depends(
        get_resume_service
    ),
):
    return await service.get_resume(
        resume_id,
        current_user.id
    )


@router.post(
    "/{resume_id}/sections",
    response_model=ResumeSectionCreateSchema,
    status_code=status.HTTP_201_CREATED,

)
async def add_section(
    resume_id: UUID,
    data: ResumeSectionCreateSchema,
    current_user: User = Depends(get_current_user),
    service: ResumeService = Depends(
    get_resume_service
    ),
):

    return await service.add_section(
        resume_id=resume_id,
        user_id=current_user.id,
        data=data,
    )