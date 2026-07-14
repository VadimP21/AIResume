"""Содержит компоненты модуля test_fake_auth_route."""

from typing import Any

import pytest
from fastapi import APIRouter, FastAPI
from fastapi.testclient import TestClient
from pydantic import ValidationError

from app.api.v1.auth.dependencies import get_auth_service
from app.api.v1.auth.router import _register_fake_auth_route
from app.core.config import Settings, get_settings


def make_settings(**overrides: Any) -> Settings:
    """Создаёт settings."""
    values: dict[str, Any] = {
        "POSTGRES_HOST": "localhost",
        "POSTGRES_DB": "test",
        "POSTGRES_USER": "test",
        "POSTGRES_PASSWORD": "test",
        "REDIS_HOST": "localhost",
        "REDIS_PASSWORD": "test",
        "JWT_SECRET": "test-secret-at-least-32-characters",
    }
    values.update(overrides)
    return Settings(**values)


def route_paths(auth_router: APIRouter) -> set[str]:
    """Выполняет операцию route paths."""
    return {route.path for route in auth_router.routes}


@pytest.mark.parametrize("app_env", ["development", "test"])
def test_fake_auth_route_requires_explicit_flag(app_env: str) -> None:
    """Проверяет сценарий fake auth route requires explicit flag."""
    app_settings = make_settings(APP_ENV=app_env, ENABLE_FAKE_AUTH=False)
    auth_router = APIRouter()

    _register_fake_auth_route(auth_router, app_settings)

    assert "/fake_auth" not in route_paths(auth_router)


@pytest.mark.parametrize("app_env", ["development", "test"])
def test_fake_auth_route_is_available_in_allowed_environment(app_env: str) -> None:
    """Проверяет сценарий fake auth route is available in allowed environment."""
    app_settings = make_settings(
        APP_ENV=app_env,
        ENABLE_FAKE_AUTH=True,
        FAKE_AUTH_EMAIL="developer@example.com",
        FAKE_AUTH_PASSWORD="configured-password",
    )
    auth_router = APIRouter()

    _register_fake_auth_route(auth_router, app_settings)

    assert "/fake_auth" in route_paths(auth_router)


@pytest.mark.parametrize("app_env", ["staging", "production"])
def test_fake_auth_cannot_be_enabled_outside_allowed_environment(
    app_env: str,
) -> None:
    """Проверяет сценарий fake auth cannot be enabled outside allowed environment."""
    with pytest.raises(
        ValidationError,
        match="ENABLE_FAKE_AUTH is allowed only in development or test",
    ):
        make_settings(
            APP_ENV=app_env,
            ENABLE_FAKE_AUTH=True,
            FAKE_AUTH_EMAIL="developer@example.com",
            FAKE_AUTH_PASSWORD="configured-password",
        )


def test_fake_auth_requires_configured_credentials() -> None:
    """Проверяет сценарий fake auth requires configured credentials."""
    with pytest.raises(
        ValidationError,
        match="FAKE_AUTH_EMAIL and FAKE_AUTH_PASSWORD are required",
    ):
        make_settings(
            APP_ENV="development",
            ENABLE_FAKE_AUTH=True,
        )


def test_fake_auth_endpoint_uses_configured_credentials() -> None:
    """Проверяет сценарий fake auth endpoint uses configured credentials."""
    app_settings = make_settings(
        APP_ENV="development",
        ENABLE_FAKE_AUTH=True,
        FAKE_AUTH_EMAIL="developer@example.com",
        FAKE_AUTH_PASSWORD="configured-password",
    )
    received_credentials: list[tuple[str, str]] = []

    class FakeAuthService:
        """Представляет сущность FakeAuthService."""

        async def fake_auth(self, email: str, password: str) -> dict[str, str]:
            """Выполняет операцию fake auth."""
            received_credentials.append((email, password))
            return {
                "access_token": "access-token",
                "refresh_token": "refresh-token",
            }

    auth_router = APIRouter()
    _register_fake_auth_route(auth_router, app_settings)
    app = FastAPI()
    app.include_router(auth_router)
    app.dependency_overrides[get_auth_service] = lambda: FakeAuthService()
    app.dependency_overrides[get_settings] = lambda: app_settings

    with TestClient(app) as client:
        response = client.post("/fake_auth")

    assert response.status_code == 200
    assert received_credentials == [("developer@example.com", "configured-password")]
