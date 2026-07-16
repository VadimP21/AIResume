"""Тесты HTTP-импорта и экспорта резюме."""

from datetime import UTC, datetime
from types import SimpleNamespace
from unittest.mock import AsyncMock
from uuid import uuid4

from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.api.v1.auth.dependencies import get_current_user
from app.api.v1.resumes.dependencies import get_resume_service
from app.api.v1.resumes.router import router
from app.core.exceptions import (
    AppException,
    NotFoundException,
    ServiceUnavailableException,
    ValidationException,
    app_exception_handler,
)


def make_app(service: object | None = None) -> FastAPI:
    """Создаёт приложение с тестовыми зависимостями."""
    app = FastAPI()
    app.include_router(router)
    app.add_exception_handler(AppException, app_exception_handler)
    if service is not None:
        app.dependency_overrides[get_resume_service] = lambda: service
        app.dependency_overrides[get_current_user] = lambda: SimpleNamespace(id=uuid4())
    return app


def response_resume() -> SimpleNamespace:
    """Возвращает DTO резюме для API-ответа."""
    now = datetime.now(UTC)
    return SimpleNamespace(
        id=uuid4(),
        title="Imported",
        created_at=now,
        updated_at=now,
        sections=[],
    )


def test_export_requires_authentication() -> None:
    """Не экспортирует резюме без аутентификации."""
    with TestClient(make_app()) as client:
        response = client.get(f"/resumes/{uuid4()}/export?format=docx")

    assert response.status_code == 401


def test_export_returns_docx_attachment() -> None:
    """Возвращает DOCX как вложение."""
    service = SimpleNamespace(
        export_resume=AsyncMock(return_value=(b"docx", "resume.docx"))
    )
    with TestClient(make_app(service)) as client:
        response = client.get(f"/resumes/{uuid4()}/export?format=docx")

    assert response.status_code == 200
    assert response.headers["content-type"].startswith(
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    )
    assert "attachment;" in response.headers["content-disposition"]
    assert response.content == b"docx"


def test_export_returns_pdf_attachment() -> None:
    """Возвращает PDF как вложение."""
    service = SimpleNamespace(
        export_resume=AsyncMock(return_value=(b"pdf", "resume.pdf"))
    )
    with TestClient(make_app(service)) as client:
        response = client.get(f"/resumes/{uuid4()}/export?format=pdf")

    assert response.status_code == 200
    assert response.headers["content-type"].startswith("application/pdf")
    assert "attachment;" in response.headers["content-disposition"]
    assert response.content == b"pdf"


def test_export_returns_503_when_pdf_renderer_is_unavailable() -> None:
    """Не раскрывает системную ошибку PDF-рендера клиенту."""
    service = SimpleNamespace(
        export_resume=AsyncMock(
            side_effect=ServiceUnavailableException(
                "PDF export is temporarily unavailable"
            )
        )
    )
    with TestClient(make_app(service)) as client:
        response = client.get(f"/resumes/{uuid4()}/export?format=pdf")

    assert response.status_code == 503
    assert response.json() == {"detail": "PDF export is temporarily unavailable"}


def test_export_hides_resume_of_another_user() -> None:
    """Не экспортирует резюме, недоступное текущему пользователю."""
    service = SimpleNamespace(
        export_resume=AsyncMock(side_effect=NotFoundException("Resume not found"))
    )
    with TestClient(make_app(service)) as client:
        response = client.get(f"/resumes/{uuid4()}/export?format=docx")

    assert response.status_code == 404


def test_import_returns_created_resume() -> None:
    """Создаёт резюме из multipart-файла."""
    service = SimpleNamespace(import_resume=AsyncMock(return_value=response_resume()))
    with TestClient(make_app(service)) as client:
        response = client.post(
            "/resumes/import",
            files={
                "file": (
                    "resume.docx",
                    b"document",
                    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                )
            },
        )

    assert response.status_code == 201
    service.import_resume.assert_awaited_once()


def test_import_returns_422_for_invalid_file() -> None:
    """Возвращает 422 для ошибки проверки импортируемого файла."""
    service = SimpleNamespace(
        import_resume=AsyncMock(
            side_effect=ValidationException("Unsupported file format")
        )
    )
    with TestClient(make_app(service)) as client:
        response = client.post(
            "/resumes/import",
            files={"file": ("resume.pdf", b"bad", "application/pdf")},
        )

    assert response.status_code == 422
    assert response.json() == {"detail": "Unsupported file format"}


def test_import_returns_503_when_ai_provider_is_unavailable() -> None:
    """Сохраняет контракт 503 при недоступности AI-провайдера."""
    service = SimpleNamespace(
        import_resume=AsyncMock(
            side_effect=ServiceUnavailableException(
                "Resume import is temporarily unavailable"
            )
        )
    )
    with TestClient(make_app(service)) as client:
        response = client.post(
            "/resumes/import",
            files={
                "file": (
                    "resume.docx",
                    b"document",
                    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                )
            },
        )

    assert response.status_code == 503
    assert response.json() == {"detail": "Resume import is temporarily unavailable"}
