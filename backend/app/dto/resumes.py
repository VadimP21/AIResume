"""Содержит DTO и команды для резюме и его секций."""

from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum
from typing import Any
from uuid import UUID

from app.dto.common import UNSET, UnsetType


class SectionType(StrEnum):
    """Перечисляет поддерживаемые типы секций резюме."""

    SUMMARY = "summary"
    EXPERIENCE = "experience"
    EDUCATION = "education"
    SKILLS = "skills"
    PROJECTS = "projects"
    LANGUAGES = "languages"


@dataclass(frozen=True, slots=True)
class CreateResumeCommand:
    """Содержит данные для создания резюме."""

    title: str


@dataclass(frozen=True, slots=True)
class UpdateResumeCommand:
    """Содержит изменения резюме с сохранением семантики PATCH."""

    title: str | None | UnsetType = UNSET


@dataclass(frozen=True, slots=True)
class CreateSectionCommand:
    """Содержит данные для создания секции резюме."""

    section_type: SectionType
    content: dict[str, Any]


@dataclass(frozen=True, slots=True)
class UpdateSectionCommand:
    """Содержит изменения секции с сохранением семантики PATCH."""

    content: dict[str, Any] | None | UnsetType = UNSET


@dataclass(frozen=True, slots=True)
class ResumeSectionDTO:
    """Содержит данные секции резюме для чтения."""

    id: UUID
    resume_id: UUID
    section_type: SectionType
    position: int
    content: dict[str, Any]
    created_at: datetime
    updated_at: datetime


@dataclass(frozen=True, slots=True)
class ResumeDTO:
    """Содержит данные резюме для чтения."""

    id: UUID
    user_id: UUID
    title: str
    created_at: datetime
    updated_at: datetime
    sections: tuple[ResumeSectionDTO, ...]
