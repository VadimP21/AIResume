"""Тесты рендеринга резюме в документы."""

from io import BytesIO
from types import SimpleNamespace

from docx import Document

from app.services.resume_document import ResumeDocumentRenderer


def resume() -> SimpleNamespace:
    """Возвращает резюме для рендеринга."""
    return SimpleNamespace(
        title="Python Developer",
        sections=[
            SimpleNamespace(
                section_type="summary",
                content={"text": "Backend developer"},
            ),
            SimpleNamespace(
                section_type="skills",
                content={"skills": [{"name": "Python", "level": "Senior"}]},
            ),
        ],
    )


def test_renders_docx_with_resume_content() -> None:
    """Рендерит DOCX с заголовком и секциями."""
    content = ResumeDocumentRenderer().render_docx(resume())
    document = Document(BytesIO(content))
    text = "\n".join(paragraph.text for paragraph in document.paragraphs)

    assert "Python Developer" in text
    assert "Backend developer" in text
    assert "Python" in text
