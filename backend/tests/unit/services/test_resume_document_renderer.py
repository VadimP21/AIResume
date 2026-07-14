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


def test_renders_docx_with_resume_content() -> None:
    """Рендерит DOCX с заголовком и секциями."""
    content = ResumeDocumentRenderer().render_docx(resume())
    document = Document(BytesIO(content))
    text = "\n".join(paragraph.text for paragraph in document.paragraphs)

    assert "Python Developer" in text
    assert "Backend developer" in text
    assert "Python" in text


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
