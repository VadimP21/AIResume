"""Содержит компоненты модуля section."""

from datetime import date
from typing import Annotated, Literal

from pydantic import BaseModel, Field

from app.models.resume_section import SectionType


class SummaryContent(BaseModel):
    """Представляет сущность SummaryContent."""

    text: str


class ExperienceItem(BaseModel):
    """Представляет сущность ExperienceItem."""

    company: str
    position: str
    start_date: date
    end_date: date | None = None
    description: str | None = None


class ExperienceContent(BaseModel):
    """Представляет сущность ExperienceContent."""

    experiences: list[ExperienceItem]


class SkillItem(BaseModel):
    """Представляет сущность SkillItem."""

    name: str
    level: str | None = None


class SkillsContent(BaseModel):
    """Представляет сущность SkillsContent."""

    skills: list[SkillItem]


class SummarySection(BaseModel):
    """Представляет сущность SummarySection."""

    section_type: Literal[SectionType.SUMMARY]

    content: SummaryContent


class ExperienceSection(BaseModel):
    """Представляет сущность ExperienceSection."""

    section_type: Literal[SectionType.EXPERIENCE]

    content: ExperienceContent


class SkillsSection(BaseModel):
    """Представляет сущность SkillsSection."""

    section_type: Literal[SectionType.SKILLS]

    content: SkillsContent


SectionContent = Annotated[
    SummarySection | ExperienceSection | SkillsSection,
    Field(discriminator="section_type"),
]
