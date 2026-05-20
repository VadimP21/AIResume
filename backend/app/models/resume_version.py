from sqlalchemy import ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base
from app.db.mixins import UUIDMixin, TimestampMixin


class ResumeVersion(Base,
             UUIDMixin,
             TimestampMixin,
             ):
    __tablename__ = "resume_versions"

    resume_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(
            "resumes.id",
            ondelete="CASCADE",
        ),
        nullable=False,
        index=True,
    )

    snapshot: Mapped[dict] = mapped_column(
        JSONB,
        nullable=False,
    )
