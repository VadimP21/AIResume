from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.testclient import TestClient
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.api.v1.health import router as health_module


def make_app() -> FastAPI:
    app = FastAPI()
    app.include_router(health_module.router)
    return app


def test_healthcheck_returns_503_when_database_is_unavailable(
    monkeypatch,
) -> None:
    @asynccontextmanager
    async def failed_session():
        raise RuntimeError("database unavailable")
        yield

    async def healthy_ping() -> None:
        return None

    monkeypatch.setattr(health_module, "AsyncSessionLocal", failed_session)
    monkeypatch.setattr(health_module.redis_client, "ping", healthy_ping)

    with TestClient(make_app()) as client:
        response = client.get("/health")

    assert response.status_code == 503
    assert response.json() == {"status": "error", "database": "error", "redis": "ok"}


def test_healthcheck_returns_503_when_redis_is_unavailable(
    monkeypatch,
) -> None:
    class Session:
        async def execute(self, statement):
            return None

    @asynccontextmanager
    async def healthy_session():
        yield Session()

    async def failed_ping() -> None:
        raise RuntimeError("redis unavailable")

    monkeypatch.setattr(health_module, "AsyncSessionLocal", healthy_session)
    monkeypatch.setattr(health_module.redis_client, "ping", failed_ping)

    with TestClient(make_app()) as client:
        response = client.get("/health")

    assert response.status_code == 503
    assert response.json() == {"status": "error", "database": "ok", "redis": "error"}


def test_healthcheck_returns_ok_with_real_dependencies(
    monkeypatch,
    test_session_factory: async_sessionmaker[AsyncSession],
    test_redis: Redis,
) -> None:
    monkeypatch.setattr(health_module, "AsyncSessionLocal", test_session_factory)
    monkeypatch.setattr(health_module, "redis_client", test_redis)

    with TestClient(make_app()) as client:
        response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok", "database": "ok", "redis": "ok"}
