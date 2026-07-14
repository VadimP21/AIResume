"""Содержит компоненты модуля test_dependencies."""

from collections.abc import AsyncIterator
from types import SimpleNamespace
from uuid import uuid4

import pytest
from fastapi import Depends, FastAPI
from fastapi.testclient import TestClient

from app.api.v1.auth import dependencies
from app.core.security import create_access_token, create_refresh_token
from app.db.session import get_db


@pytest.fixture
def protected_client(
    monkeypatch: pytest.MonkeyPatch,
) -> tuple[TestClient, SimpleNamespace]:
    """Выполняет операцию protected client."""
    user = SimpleNamespace(
        id=uuid4(),
        token_version=1,
        is_active=True,
    )

    class FakeUserRepository:
        """Представляет сущность FakeUserRepository."""

        def __init__(self, session: object) -> None:
            """Инициализирует экземпляр."""
            self.session = session

        async def get_by_id(self, user_id: object) -> SimpleNamespace | None:
            """Возвращает by id."""
            return user if user_id == user.id else None

    async def override_get_db() -> AsyncIterator[object]:
        """Выполняет операцию override get db."""
        yield object()

    app = FastAPI()
    app.dependency_overrides[get_db] = override_get_db
    monkeypatch.setattr(dependencies, "UserRepository", FakeUserRepository)

    @app.get("/protected")
    async def protected(
        current_user: object = Depends(dependencies.get_current_user),
    ) -> dict[str, str]:
        """Выполняет операцию protected."""
        return {"user_id": str(current_user.id)}

    return TestClient(app), user


def test_protected_endpoint_accepts_access_token(
    protected_client: tuple[TestClient, SimpleNamespace],
) -> None:
    """Проверяет сценарий protected endpoint accepts access token."""
    client, user = protected_client
    access_token = create_access_token(str(user.id), user.token_version)

    response = client.get(
        "/protected",
        headers={"Authorization": f"Bearer {access_token}"},
    )

    assert response.status_code == 200
    assert response.json() == {"user_id": str(user.id)}


def test_protected_endpoint_rejects_refresh_token(
    protected_client: tuple[TestClient, SimpleNamespace],
) -> None:
    """Проверяет сценарий protected endpoint rejects refresh token."""
    client, user = protected_client
    refresh_token, _ = create_refresh_token(str(user.id), user.token_version)

    response = client.get(
        "/protected",
        headers={"Authorization": f"Bearer {refresh_token}"},
    )

    assert response.status_code == 401
    assert response.json() == {"detail": "Invalid token type"}
