"""Содержит компоненты модуля resume."""

from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.models.resume_section import SectionType
from app.schemas.section import SectionContent


class ResumeCreateSchema(BaseModel):
    """Представляет сущность ResumeCreateSchema."""

    title: str = Field(min_length=1, max_length=255)


class ResumeUpdateSchema(BaseModel):
    """Представляет сущность ResumeUpdateSchema."""

    title: str | None = Field(
        default=None,
        min_length=1,
        max_length=255,
    )


class ResumeSectionCreateSchema(BaseModel):
    """Представляет сущность ResumeSectionCreateSchema."""

    section: SectionContent


class ResumeSectionUpdateSchema(BaseModel):
    """Представляет сущность ResumeSectionUpdateSchema."""

    content: dict[str, Any]


class ResumeSectionResponseSchema(BaseModel):
    """Представляет сущность ResumeSectionResponseSchema."""

    id: UUID
    section_type: SectionType
    position: int
    content: dict[str, Any]

    model_config = ConfigDict(from_attributes=True)


class ResumeResponseSchema(BaseModel):
    """Представляет сущность ResumeResponseSchema."""

    id: UUID
    title: str
    created_at: datetime
    updated_at: datetime

    sections: list[ResumeSectionResponseSchema]

    model_config = ConfigDict(from_attributes=True)


class ResumeListResponseSchema(BaseModel):
    """Представляет сущность ResumeListResponseSchema."""

    id: UUID
    title: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ResumeVersionListResponseSchema(BaseModel):
    """Представляет краткие сведения о версии резюме."""

    id: UUID
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ResumeVersionResponseSchema(ResumeVersionListResponseSchema):
    """Представляет полное содержимое версии резюме."""

    resume_id: UUID
    snapshot: dict[str, object]
