from uuid import UUID
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict

from app.models.resume_section import SectionType


class ResumeCreateSchema(BaseModel):
    title: str = Field(min_length=1, max_length=255)


class ResumeUpdateSchema(BaseModel):
    title: str | None = Field(
        default=None,
        min_length=1,
        max_length=255,
    )

class ResumeSectionCreateSchema(BaseModel):
    type: SectionType
    content: dict


class ResumeSectionUpdateSchema(BaseModel):
    content: dict


class ResumeSectionResponseSchema(BaseModel):
    id: UUID
    type: SectionType
    position: int
    content: dict

    model_config = ConfigDict(
        from_attributes=True
    )


class ResumeResponseSchema(BaseModel):
    id: UUID
    title: str
    created_at: datetime
    updated_at: datetime

    sections: list[ResumeSectionResponseSchema]

    model_config = ConfigDict(
        from_attributes=True
    )