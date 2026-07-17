"""Содержит HTTP-тесты истории версий резюме."""

from datetime import UTC, datetime
from types import SimpleNamespace
from unittest.mock import AsyncMock
from uuid import uuid4

from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.api.v1.auth.dependencies import get_current_user
from app.api.v1.resumes.dependencies import get_resume_service
from app.api.v1.resumes.router import router
from app.core.exceptions import AppException, app_exception_handler


def make_app(service: object | None = None) -> FastAPI:
    """Создаёт приложение с тестовыми зависимостями."""
    app = FastAPI()
    app.include_router(router)
    app.add_exception_handler(AppException, app_exception_handler)
    if service is not None:
        app.dependency_overrides[get_resume_service] = lambda: service
        app.dependency_overrides[get_current_user] = lambda: SimpleNamespace(id=uuid4())
    return app


def make_version() -> SimpleNamespace:
    """Создаёт DTO версии резюме."""
    return SimpleNamespace(
        id=uuid4(),
        resume_id=uuid4(),
        created_at=datetime.now(UTC),
        snapshot={"resume": {"title": "Resume"}, "sections": []},
    )


def test_list_versions_requires_authentication() -> None:
    """Не возвращает историю версий без аутентификации."""
    with TestClient(make_app()) as client:
        response = client.get(f"/resumes/{uuid4()}/versions")

    assert response.status_code == 401


def test_list_versions_passes_pagination_to_service() -> None:
    """Передаёт параметры пагинации в сервис."""
    service = SimpleNamespace(list_versions=AsyncMock(return_value=[make_version()]))
    resume_id = uuid4()
    with TestClient(make_app(service)) as client:
        response = client.get(f"/resumes/{resume_id}/versions?limit=10&offset=5")

    assert response.status_code == 200
    assert len(response.json()) == 1
    assert service.list_versions.await_args.args[0] == resume_id
    assert service.list_versions.await_args.args[2:] == (10, 5)


def test_get_version_returns_snapshot() -> None:
    """Возвращает полное содержимое выбранной версии."""
    version = make_version()
    service = SimpleNamespace(get_version=AsyncMock(return_value=version))
    with TestClient(make_app(service)) as client:
        response = client.get(f"/resumes/{version.resume_id}/versions/{version.id}")

    assert response.status_code == 200
    assert response.json()["snapshot"] == version.snapshot


def test_restore_version_returns_restored_resume() -> None:
    """Возвращает резюме после восстановления версии."""
    now = datetime.now(UTC)
    restored = SimpleNamespace(
        id=uuid4(),
        title="Restored",
        created_at=now,
        updated_at=now,
        sections=[],
    )
    service = SimpleNamespace(restore_version=AsyncMock(return_value=restored))
    version_id = uuid4()
    with TestClient(make_app(service)) as client:
        response = client.post(f"/resumes/{restored.id}/versions/{version_id}/restore")

    assert response.status_code == 200
    assert response.json()["title"] == "Restored"
