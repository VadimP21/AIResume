"""Тесты схем содержимого секций резюме."""

from pydantic import TypeAdapter

from app.models.resume_section import SectionType
from app.schemas.section import SectionContent


def test_validates_education_section() -> None:
    """Валидирует обязательные поля секции образования."""
    section = TypeAdapter(SectionContent).validate_python(
        {
            "section_type": "education",
            "content": {
                "education": [
                    {
                        "institution": "State University",
                        "degree": "Bachelor",
                        "field": "Computer Science",
                        "start_date": "2019-09-01",
                        "end_date": None,
                    }
                ]
            },
        }
    )

    assert section.section_type is SectionType.EDUCATION
    assert section.content.education[0].end_date is None


def test_validates_project_section() -> None:
    """Валидирует проект с необязательными описанием и ссылкой."""
    section = TypeAdapter(SectionContent).validate_python(
        {
            "section_type": "projects",
            "content": {"projects": [{"name": "AI Resume"}]},
        }
    )

    assert section.section_type is SectionType.PROJECTS
    assert section.content.projects[0].description is None
    assert section.content.projects[0].url is None


def test_validates_language_section() -> None:
    """Валидирует обязательные поля секции языков."""
    section = TypeAdapter(SectionContent).validate_python(
        {
            "section_type": "languages",
            "content": {"languages": [{"name": "English", "level": "C1"}]},
        }
    )

    assert section.section_type is SectionType.LANGUAGES
    assert section.content.languages[0].level == "C1"
