"""Тесты извлечения текста из файлов резюме."""

from io import BytesIO

import pytest
from docx import Document
from pypdf import PdfWriter

from app.core.exceptions import ValidationException
from app.services.resume_file import ResumeFileExtractor


def make_docx(text: str) -> bytes:
    """Создаёт DOCX с текстом."""
    document = Document()
    document.add_paragraph(text)
    stream = BytesIO()
    document.save(stream)
    return stream.getvalue()


def test_extracts_text_from_docx() -> None:
    """Извлекает текст из DOCX."""
    extractor = ResumeFileExtractor(max_file_size=5 * 1024 * 1024)

    assert extractor.extract("resume.docx", make_docx("Python developer")) == (
        "Python developer"
    )


def test_rejects_file_with_unknown_signature() -> None:
    """Отклоняет файл неподдерживаемого формата."""
    extractor = ResumeFileExtractor(max_file_size=5 * 1024 * 1024)

    with pytest.raises(ValidationException, match="Unsupported file format"):
        extractor.extract("resume.pdf", b"not a document")


def test_rejects_empty_file() -> None:
    """Отклоняет пустой файл."""
    extractor = ResumeFileExtractor(max_file_size=5 * 1024 * 1024)

    with pytest.raises(ValidationException, match="File is empty"):
        extractor.extract("resume.pdf", b"")


def test_rejects_file_larger_than_limit() -> None:
    """Отклоняет файл больше установленного лимита."""
    extractor = ResumeFileExtractor(max_file_size=4)

    with pytest.raises(ValidationException, match="File is too large"):
        extractor.extract("resume.pdf", b"%PDF-1.7")


def test_rejects_pdf_without_text_layer() -> None:
    """Отклоняет PDF без текстового слоя."""
    stream = BytesIO()
    writer = PdfWriter()
    writer.add_blank_page(width=100, height=100)
    writer.write(stream)
    extractor = ResumeFileExtractor(max_file_size=5 * 1024 * 1024)

    with pytest.raises(ValidationException, match="does not contain text"):
        extractor.extract("resume.pdf", stream.getvalue())
