import asyncio
from types import SimpleNamespace
from uuid import uuid4

import pytest
from fastapi import HTTPException

from app.api.v1.auth.schemas import RefreshRequest
from app.services import auth_service
from app.services.auth_service import CONSUME_REFRESH_TOKEN_SCRIPT, AuthService


class InMemoryRefreshRedis:
    def __init__(self, values: dict[str, str]) -> None:
        self.values = values
        self.set_calls: list[tuple[str, str, int]] = []
        self._lock = asyncio.Lock()

    async def get(self, key: str) -> str | None:
        return self.values.get(key)

    async def eval(
        self,
        script: str,
        numkeys: int,
        key: str,
        expected_hash: str,
    ) -> int:
        assert script == CONSUME_REFRESH_TOKEN_SCRIPT
        assert numkeys == 1

        async with self._lock:
            if self.values.get(key) != expected_hash:
                return 0
            del self.values[key]
            return 1

    async def set(self, key: str, value: str, *, ex: int) -> None:
        self.values[key] = value
        self.set_calls.append((key, value, ex))


class BarrierUserRepository:
    def __init__(self, user: SimpleNamespace) -> None:
        self.user = user
        self._requests = 0
        self._both_requests_ready = asyncio.Event()

    async def get_by_id(self, user_id: object) -> SimpleNamespace | None:
        self._requests += 1
        if self._requests == 2:
            self._both_requests_ready.set()

        await self._both_requests_ready.wait()
        return self.user if user_id == self.user.id else None


@pytest.mark.asyncio
async def test_refresh_token_rotation_allows_only_one_parallel_request(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    user = SimpleNamespace(id=uuid4(), token_version=1, is_active=True)
    jti = "original-jti"
    refresh_key = f"refresh:{user.id}:{jti}"
    redis = InMemoryRefreshRedis({refresh_key: "stored-hash"})
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
        auth_service, "create_access_token", lambda subject, tv: "access"
    )
    monkeypatch.setattr(
        auth_service,
        "create_refresh_token",
        lambda subject, tv: ("new-refresh", "new-jti"),
    )
    monkeypatch.setattr(auth_service, "hash_token", lambda token: "new-hash")

    results = await asyncio.gather(
        service.refresh_tokens(RefreshRequest(refresh_token="original-refresh")),
        service.refresh_tokens(RefreshRequest(refresh_token="original-refresh")),
        return_exceptions=True,
    )

    successful_results = [result for result in results if isinstance(result, dict)]
    failed_results = [result for result in results if isinstance(result, HTTPException)]

    assert successful_results == [
        {
            "access_token": "access",
            "refresh_token": "new-refresh",
        }
    ]
    assert len(failed_results) == 1
    assert failed_results[0].status_code == 401
    assert failed_results[0].detail == "Token revoked"
    assert refresh_key not in redis.values
    assert redis.values[f"refresh:{user.id}:new-jti"] == "new-hash"
    assert redis.set_calls == [
        (
            f"refresh:{user.id}:new-jti",
            "new-hash",
            auth_service.settings.REFRESH_TOKEN_EXPIRE_SECONDS,
        )
    ]
