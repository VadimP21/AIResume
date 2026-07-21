"""Содержит компоненты модуля section."""

from datetime import date
from typing import Annotated, Literal

from pydantic import BaseModel, Field

from app.dto.resumes import SectionType


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


class EducationItem(BaseModel):
    """Представляет элемент образования."""

    institution: str
    degree: str
    field: str
    start_date: date
    end_date: date | None = None


class EducationContent(BaseModel):
    """Представляет содержимое секции образования."""

    education: list[EducationItem]


class SkillItem(BaseModel):
    """Представляет сущность SkillItem."""

    name: str
    level: str | None = None


class SkillsContent(BaseModel):
    """Представляет сущность SkillsContent."""

    skills: list[SkillItem]


class ProjectItem(BaseModel):
    """Представляет элемент проекта."""

    name: str
    description: str | None = None
    url: str | None = None


class ProjectsContent(BaseModel):
    """Представляет содержимое секции проектов."""

    projects: list[ProjectItem]


class LanguageItem(BaseModel):
    """Представляет элемент языка."""

    name: str
    level: str


class LanguagesContent(BaseModel):
    """Представляет содержимое секции языков."""

    languages: list[LanguageItem]


class SummarySection(BaseModel):
    """Представляет сущность SummarySection."""

    section_type: Literal[SectionType.SUMMARY]

    content: SummaryContent


class ExperienceSection(BaseModel):
    """Представляет сущность ExperienceSection."""

    section_type: Literal[SectionType.EXPERIENCE]

    content: ExperienceContent


class EducationSection(BaseModel):
    """Представляет сущность EducationSection."""

    section_type: Literal[SectionType.EDUCATION]

    content: EducationContent


class SkillsSection(BaseModel):
    """Представляет сущность SkillsSection."""

    section_type: Literal[SectionType.SKILLS]

    content: SkillsContent


class ProjectsSection(BaseModel):
    """Представляет сущность ProjectsSection."""

    section_type: Literal[SectionType.PROJECTS]

    content: ProjectsContent


class LanguagesSection(BaseModel):
    """Представляет сущность LanguagesSection."""

    section_type: Literal[SectionType.LANGUAGES]

    content: LanguagesContent


SectionContent = Annotated[
    SummarySection
    | ExperienceSection
    | EducationSection
    | SkillsSection
    | ProjectsSection
    | LanguagesSection,
    Field(discriminator="section_type"),
]
