from enum import Enum

from sqlalchemy import Integer, ForeignKey, Enum as SQLEnum, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.ext.mutable import MutableDict
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.db.mixins import UUIDMixin, TimestampMixin


class SectionType(str, Enum):
    SUMMARY = "summary"
    EXPERIENCE = "experience"
    EDUCATION = "education"
    SKILLS = "skills"
    PROJECTS = "projects"
    LANGUAGES = "languages"


class ResumeSection(Base,
                    UUIDMixin,
                    TimestampMixin,
                    ):
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

    resume: Mapped["Resume"] = relationship(
        back_populates="sections"
    )
