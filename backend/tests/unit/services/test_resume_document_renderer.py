"""Тесты рендеринга резюме в документы."""

from io import BytesIO
from types import SimpleNamespace

import pytest
from docx import Document

from app.core.exceptions import ServiceUnavailableException
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


def full_resume() -> SimpleNamespace:
    """Возвращает резюме со всеми секциями в пользовательском порядке."""
    return SimpleNamespace(
        title="Python <Developer>",
        sections=[
            SimpleNamespace(
                position=3,
                section_type="experience",
                content={
                    "experiences": [
                        {
                            "company": "Acme & Co",
                            "position": "Backend Developer",
                            "start_date": "2024-01-01",
                            "end_date": None,
                            "description": "Built APIs",
                        }
                    ]
                },
            ),
            SimpleNamespace(
                position=1,
                section_type="summary",
                content={"text": "ATS-friendly summary"},
            ),
            SimpleNamespace(
                position=2,
                section_type="education",
                content={
                    "education": [
                        {
                            "institution": "State University",
                            "degree": "Bachelor",
                            "field": "Computer Science",
                            "start_date": "2019-09-01",
                            "end_date": "2023-06-30",
                        }
                    ]
                },
            ),
            SimpleNamespace(
                position=4,
                section_type="skills",
                content={"skills": [{"name": "Python", "level": "Senior"}]},
            ),
            SimpleNamespace(
                position=5,
                section_type="projects",
                content={
                    "projects": [
                        {
                            "name": "AI Resume",
                            "description": "Resume builder",
                            "url": "https://example.com/resume",
                        }
                    ]
                },
            ),
            SimpleNamespace(
                position=6,
                section_type="languages",
                content={"languages": [{"name": "English", "level": "C1"}]},
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


def test_renders_all_sections_in_position_order_for_docx() -> None:
    """Рендерит все секции DOCX в порядке позиции и без пустых полей."""
    content = ResumeDocumentRenderer().render_docx(full_resume())
    document = Document(BytesIO(content))
    text = "\n".join(paragraph.text for paragraph in document.paragraphs)

    expected_parts = [
        "Python <Developer>",
        "Summary",
        "Education",
        "Experience",
        "Skills",
        "Projects",
        "Languages",
        "2019-09-01 — 2023-06-30",
        "2024-01-01 — Present",
        "https://example.com/resume",
    ]
    indices = [text.index(part) for part in expected_parts[:7]]

    assert all(part in text for part in expected_parts)
    assert indices == sorted(indices)
    assert "None" not in text


def test_renders_all_sections_as_escaped_html_in_position_order() -> None:
    """Строит экранированный HTML со всеми секциями в порядке позиции."""
    html = ResumeDocumentRenderer()._render_html(full_resume())

    expected_headings = [
        "Summary",
        "Education",
        "Experience",
        "Skills",
        "Projects",
        "Languages",
    ]
    indices = [html.index(heading) for heading in expected_headings]

    assert "Python &lt;Developer&gt;" in html
    assert "Acme &amp; Co" in html
    assert "2024-01-01 — Present" in html
    assert indices == sorted(indices)


def test_renders_all_sections_for_pdf(monkeypatch: pytest.MonkeyPatch) -> None:
    """Передаёт в PDF-движок HTML со всеми секциями резюме."""
    rendered_html: list[str] = []

    class Html:
        """Имитирует HTML-объект WeasyPrint."""

        def __init__(self, string: str) -> None:
            """Сохраняет HTML для проверки."""
            self.string = string
            rendered_html.append(string)

        def write_pdf(self) -> bytes:
            """Возвращает содержимое тестового PDF."""
            return b"pdf"

    original_import = __import__

    def import_weasyprint(
        name: str,
        *args: object,
        **kwargs: object,
    ) -> object:
        """Подменяет WeasyPrint тестовой реализацией."""
        if name == "weasyprint":
            return SimpleNamespace(HTML=Html)
        return original_import(name, *args, **kwargs)

    monkeypatch.setattr("builtins.__import__", import_weasyprint)

    assert ResumeDocumentRenderer().render_pdf(full_resume()) == b"pdf"
    html = rendered_html[0]
    assert all(
        heading in html
        for heading in (
            "Summary",
            "Education",
            "Experience",
            "Skills",
            "Projects",
            "Languages",
        )
    )


def test_pdf_render_translates_missing_system_library_to_service_error(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Не раскрывает ошибку загрузки системной библиотеки WeasyPrint."""
    original_import = __import__

    def raise_weasyprint_import_error(
        name: str,
        *args: object,
        **kwargs: object,
    ) -> object:
        """Имитирует недоступность нативной зависимости WeasyPrint."""
        if name == "weasyprint":
            raise OSError("cannot load library 'libgobject-2.0-0'")
        return original_import(name, *args, **kwargs)

    monkeypatch.setattr("builtins.__import__", raise_weasyprint_import_error)

    with pytest.raises(
        ServiceUnavailableException,
        match="PDF export is temporarily unavailable",
    ):
        ResumeDocumentRenderer().render_pdf(resume())
