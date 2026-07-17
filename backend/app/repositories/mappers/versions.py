"""Содержит мапперы ORM-версий резюме во внутренние DTO."""

from app.dto.versions import ResumeVersionDTO
from app.models.resume_version import ResumeVersion


def version_to_dto(version: ResumeVersion) -> ResumeVersionDTO:
    """Преобразует ORM-версию резюме во внутренний DTO."""
    return ResumeVersionDTO(
        id=version.id,
        resume_id=version.resume_id,
        snapshot=version.snapshot,
        created_at=version.created_at,
    )
