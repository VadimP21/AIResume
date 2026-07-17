"""Содержит компоненты модуля router."""

from typing import Annotated, Literal
from uuid import UUID

from fastapi import APIRouter, Depends, File, Query, UploadFile
from fastapi.responses import Response
from starlette import status

from app.api.v1.auth.dependencies import get_current_user
from app.api.v1.resumes.dependencies import (
    get_resume_service,
)
from app.core.config import settings
from app.models.resume import Resume
from app.models.resume_section import ResumeSection
from app.models.resume_version import ResumeVersion
from app.models.user import User
from app.schemas.resume import (
    ResumeCreateSchema,
    ResumeResponseSchema,
    ResumeSectionCreateSchema,
    ResumeSectionResponseSchema,
    ResumeSectionUpdateSchema,
    ResumeUpdateSchema,
    ResumeVersionListResponseSchema,
    ResumeVersionResponseSchema,
)
from app.services.resume import ResumeService

router = APIRouter(
    prefix="/resumes",
    tags=["Resumes"],
)

EXPORT_MEDIA_TYPES = {
    "pdf": "application/pdf",
    "docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
}


@router.post(
    "/import",
    response_model=ResumeResponseSchema,
    status_code=status.HTTP_201_CREATED,
)
async def import_resume(
    file: Annotated[UploadFile, File()],
    service: Annotated[ResumeService, Depends(get_resume_service)],
    current_user: User = Depends(get_current_user),
) -> Resume | None:
    """Импортирует новое резюме из PDF или DOCX."""
    content = await file.read(settings.RESUME_IMPORT_MAX_FILE_SIZE + 1)
    return await service.import_resume(
        user_id=current_user.id,
        filename=file.filename or "resume",
        content=content,
    )


@router.get("/{resume_id}/export")
async def export_resume(
    resume_id: UUID,
    format: Literal["pdf", "docx"],
    current_user: User = Depends(get_current_user),
    service: ResumeService = Depends(get_resume_service),
) -> Response:
    """Экспортирует резюме текущего пользователя."""
    content, filename = await service.export_resume(
        resume_id=resume_id,
        user_id=current_user.id,
        export_format=format,
    )
    return Response(
        content=content,
        media_type=EXPORT_MEDIA_TYPES[format],
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
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
) -> Resume | None:
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
) -> Resume:
    """Возвращает resume."""
    return await service.get_resume(resume_id, current_user.id)


@router.get(
    "/{resume_id}/versions",
    response_model=list[ResumeVersionListResponseSchema],
)
async def list_versions(
    resume_id: UUID,
    current_user: User = Depends(get_current_user),
    service: ResumeService = Depends(get_resume_service),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
) -> list[ResumeVersion]:
    """Возвращает историю версий резюме владельца."""
    return await service.list_versions(resume_id, current_user.id, limit, offset)


@router.get(
    "/{resume_id}/versions/{version_id}",
    response_model=ResumeVersionResponseSchema,
)
async def get_version(
    resume_id: UUID,
    version_id: UUID,
    current_user: User = Depends(get_current_user),
    service: ResumeService = Depends(get_resume_service),
) -> ResumeVersion:
    """Возвращает полное содержимое версии резюме владельца."""
    return await service.get_version(resume_id, version_id, current_user.id)


@router.post(
    "/{resume_id}/versions/{version_id}/restore",
    response_model=ResumeResponseSchema,
)
async def restore_version(
    resume_id: UUID,
    version_id: UUID,
    current_user: User = Depends(get_current_user),
    service: ResumeService = Depends(get_resume_service),
) -> Resume:
    """Восстанавливает резюме из версии владельца."""
    return await service.restore_version(resume_id, version_id, current_user.id)


@router.patch(
    "/{resume_id}",
    response_model=ResumeResponseSchema,
)
async def update_resume(
    resume_id: UUID,
    data: ResumeUpdateSchema,
    current_user: User = Depends(get_current_user),
    service: ResumeService = Depends(get_resume_service),
) -> Resume:
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
) -> None:
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
) -> ResumeSection:
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
) -> ResumeSection:
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
) -> list[Resume]:
    """Выполняет операцию list resumes."""
    return await service.get_list_resumes(current_user.id, limit, offset)
