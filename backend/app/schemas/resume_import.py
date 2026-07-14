"""Содержит DTO результата AI-импорта резюме."""

from pydantic import BaseModel, Field

from app.schemas.section import SectionContent


class ImportedResumeSchema(BaseModel):
    """Представляет структурированные данные импортированного резюме."""

    title: str = Field(min_length=1, max_length=255)
    sections: list[SectionContent] = Field(min_length=1)
