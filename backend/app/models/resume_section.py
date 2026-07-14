"""Содержит компоненты модуля resume_section."""

from enum import StrEnum
from typing import TYPE_CHECKING

from sqlalchemy import Enum as SQLEnum
from sqlalchemy import ForeignKey, Integer, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.ext.mutable import MutableDict
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.db.mixins import TimestampMixin, UUIDMixin

if TYPE_CHECKING:
    from app.models.resume import Resume


class SectionType(StrEnum):
    """Представляет сущность SectionType."""

    SUMMARY = "summary"
    EXPERIENCE = "experience"
    EDUCATION = "education"
    SKILLS = "skills"
    PROJECTS = "projects"
    LANGUAGES = "languages"


class ResumeSection(
    Base,
    UUIDMixin,
    TimestampMixin,
):
    """Представляет сущность ResumeSection."""

    __tablename__ = "resume_sections"

    __table_args__ = (
        UniqueConstraint(
            "resume_id",
            "position",
            name="uq_resume_position",
        ),
    )

    resume_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("resumes.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    section_type: Mapped[SectionType] = mapped_column(
        SQLEnum(SectionType),
        nullable=False,
    )

    position: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
    )

    content: Mapped[dict] = mapped_column(
        MutableDict.as_mutable(JSONB),
        nullable=False,
    )

    resume: Mapped["Resume"] = relationship(back_populates="sections")
