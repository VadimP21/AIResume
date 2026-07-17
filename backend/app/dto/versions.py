"""Содержит DTO версий резюме."""

from dataclasses import dataclass
from datetime import datetime
from uuid import UUID


@dataclass(frozen=True, slots=True)
class ResumeVersionDTO:
    """Содержит данные сохранённой версии резюме."""

    id: UUID
    resume_id: UUID
    snapshot: dict[str, object]
    created_at: datetime
