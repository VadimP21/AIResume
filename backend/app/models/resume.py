"""Содержит компоненты модуля resume."""

from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID as SQLAlchemyUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.db.mixins import TimestampMixin, UUIDMixin

if TYPE_CHECKING:
    from app.models.resume_section import ResumeSection


class Resume(
    Base,
    UUIDMixin,
    TimestampMixin,
):
    """Представляет сущность Resume."""

    __tablename__ = "resumes"
    # __table_args__ = (
    #     Index(
    #         "ix_resumes_user_created",
    #         "user_id",
    #         "created_at",
    #     )
    # )

    user_id: Mapped[UUID] = mapped_column(
        SQLAlchemyUUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    title: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    template_id: Mapped[UUID | None] = mapped_column(
        SQLAlchemyUUID(as_uuid=True),
        nullable=True,
    )

    sections: Mapped[list["ResumeSection"]] = relationship(
        back_populates="resume",
        cascade="all, delete-orphan",
        order_by="ResumeSection.position",
    )
