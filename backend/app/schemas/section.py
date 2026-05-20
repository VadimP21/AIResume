from datetime import date
from typing import Annotated, Literal

from pydantic import BaseModel, Field

from app.models.resume_section import SectionType


class SummaryContent(BaseModel):
    text: str


class ExperienceItem(BaseModel):
    company: str
    position: str
    start_date: date
    end_date: date | None = None
    description: str | None = None


class ExperienceContent(BaseModel):
    experiences: list[ExperienceItem]


class SkillItem(BaseModel):
    name: str
    level: str | None = None


class SkillsContent(BaseModel):
    skills: list[SkillItem]

class SummarySection(BaseModel):
    section_type: Literal[SectionType.SUMMARY]

    content: SummaryContent

class ExperienceSection(BaseModel):
    section_type: Literal[SectionType.EXPERIENCE]

    content: ExperienceContent

class SkillsSection(BaseModel):
    section_type: Literal[SectionType.SKILLS]

    content: SkillsContent

SectionContent = Annotated[
    SummarySection
    | ExperienceSection
    | SkillsSection,
    Field(discriminator="section_type"),
]