from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.models.resume_section import SectionType
from app.schemas.section import SectionContent


class ResumeCreateSchema(BaseModel):
    title: str = Field(min_length=1, max_length=255)


class ResumeUpdateSchema(BaseModel):
    title: str | None = Field(
        default=None,
        min_length=1,
        max_length=255,
    )


class ResumeSectionCreateSchema(BaseModel):
    section: SectionContent


class ResumeSectionUpdateSchema(BaseModel):
    content: dict


class ResumeSectionResponseSchema(BaseModel):
    id: UUID
    section_type: SectionType
    position: int
    content: dict

    model_config = ConfigDict(from_attributes=True)


class ResumeResponseSchema(BaseModel):
    id: UUID
    title: str
    created_at: datetime
    updated_at: datetime

    sections: list[ResumeSectionResponseSchema]

    model_config = ConfigDict(from_attributes=True)


class ResumeListResponseSchema(BaseModel):
    id: UUID
    title: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
