"""Содержит мапперы ORM-резюме и секций во внутренние DTO."""

from app.dto.resumes import ResumeDTO, ResumeSectionDTO
from app.models.resume import Resume
from app.models.resume_section import ResumeSection


def section_to_dto(section: ResumeSection) -> ResumeSectionDTO:
    """Преобразует ORM-секцию резюме во внутренний DTO."""
    return ResumeSectionDTO(
        id=section.id,
        resume_id=section.resume_id,
        section_type=section.section_type,
        position=section.position,
        content=section.content,
        created_at=section.created_at,
        updated_at=section.updated_at,
    )


def resume_to_dto(resume: Resume) -> ResumeDTO:
    """Преобразует резюме с заранее загруженными секциями во внутренний DTO."""
    return ResumeDTO(
        id=resume.id,
        user_id=resume.user_id,
        title=resume.title,
        created_at=resume.created_at,
        updated_at=resume.updated_at,
        sections=tuple(section_to_dto(section) for section in resume.sections),
    )
