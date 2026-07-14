"""Содержит компоненты модуля test_refresh_token_rotation_redis."""

import asyncio
from types import SimpleNamespace
from uuid import uuid4

import pytest
from fastapi import HTTPException
from redis.asyncio import Redis

from app.api.v1.auth.schemas import RefreshRequest
from app.services import auth_service
from app.services.auth_service import AuthService


class BarrierUserRepository:
    """Представляет сущность BarrierUserRepository."""

    def __init__(self, user: SimpleNamespace) -> None:
        """Инициализирует экземпляр."""
        self.user = user
        self._requests = 0
        self._both_requests_ready = asyncio.Event()

    async def get_by_id(self, user_id: object) -> SimpleNamespace | None:
        """Возвращает by id."""
        self._requests += 1
        if self._requests == 2:
            self._both_requests_ready.set()

        await self._both_requests_ready.wait()
        return self.user if user_id == self.user.id else None


@pytest.mark.asyncio
async def test_refresh_token_is_consumed_once_in_parallel_requests(
    monkeypatch: pytest.MonkeyPatch,
    test_redis: Redis,
) -> None:
    """Проверяет сценарий refresh token is consumed once in parallel requests."""
    redis = test_redis
    user = SimpleNamespace(id=uuid4(), token_version=1, is_active=True)
    jti = str(uuid4())
    refresh_key = f"refresh:{user.id}:{jti}"
    new_jti = str(uuid4())
    new_refresh_key = f"refresh:{user.id}:{new_jti}"
    user_repository = BarrierUserRepository(user)
    service = AuthService(user_repository, redis)
    payload = {
        "sub": str(user.id),
        "jti": jti,
        "tv": user.token_version,
        "type": "refresh",
    }
    monkeypatch.setattr(auth_service, "decode_token", lambda token: payload)
    monkeypatch.setattr(auth_service, "verify_password", lambda token, hashed: True)
    monkeypatch.setattr(
        auth_service,
        "create_access_token",
        lambda subject, tv: "access",
    )
    monkeypatch.setattr(
        auth_service,
        "create_refresh_token",
        lambda subject, tv: ("new-refresh", new_jti),
    )
    monkeypatch.setattr(auth_service, "hash_token", lambda token: "new-hash")

    try:
        await redis.set(refresh_key, "stored-hash", ex=60)

        results = await asyncio.gather(
            service.refresh_tokens(RefreshRequest(refresh_token="original-refresh")),
            service.refresh_tokens(RefreshRequest(refresh_token="original-refresh")),
            return_exceptions=True,
        )

        successful_results = [result for result in results if isinstance(result, dict)]
        failed_results = [
            result for result in results if isinstance(result, HTTPException)
        ]

        assert len(successful_results) == 1
        assert len(failed_results) == 1
        assert failed_results[0].status_code == 401
        assert await redis.get(refresh_key) is None
        assert await redis.get(new_refresh_key) == "new-hash"
    finally:
        await redis.delete(refresh_key, new_refresh_key)
