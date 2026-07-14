"""Содержит компоненты модуля auth_service."""

from typing import Protocol, cast
from uuid import UUID

from fastapi import HTTPException, status
from jose import JWTError
from redis.asyncio import Redis
from sqlalchemy.exc import IntegrityError

from app.api.v1.auth.schemas import RefreshRequest
from app.core.config import settings
from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    hash_password,
    hash_token,
    verify_password,
)
from app.repositories.user_repository import UserRepository

CONSUME_REFRESH_TOKEN_SCRIPT = """
local stored_hash = redis.call("GET", KEYS[1])
if not stored_hash or stored_hash ~= ARGV[1] then
    return 0
end

return redis.call("DEL", KEYS[1])
"""


class RefreshTokenRedis(Protocol):
    """Представляет сущность RefreshTokenRedis."""

    async def eval(
        self,
        script: str,
        numkeys: int,
        *keys_and_args: str,
    ) -> int:
        """Выполняет операцию eval."""
        ...


class AuthService:
    """Представляет сущность AuthService."""

    def __init__(
        self,
        user_repo: UserRepository,
        redis: Redis,
    ):
        """Инициализирует экземпляр."""
        self.user_repo = user_repo
        self.redis = redis

    async def register(
        self,
        email: str,
        password: str,
    ):
        """Выполняет операцию register."""
        try:
            email = email.lower().strip()
            user = await self.user_repo.create(
                email=email,
                hashed_password=hash_password(password),
            )
            await self.user_repo.session.commit()

        except IntegrityError:
            await self.user_repo.session.rollback()
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="User already exists",
            ) from None
        except Exception:
            await self.user_repo.session.rollback()
            raise

        return user

    async def login(
        self,
        email: str,
        password: str,
    ):
        """Выполняет операцию login."""
        email = email.lower().strip()
        user = await self.user_repo.get_by_email(email)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid credentials",
            )

        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User not active",
            )
        if not verify_password(
            password,
            user.hashed_password,
        ):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid credentials",
            )

        access_token = create_access_token(
            str(user.id),
            user.token_version,
        )

        refresh_token, jti = create_refresh_token(
            str(user.id),
            user.token_version,
        )

        hashed_refresh = hash_token(refresh_token)

        await self.redis.set(
            f"refresh:{user.id}:{jti}",
            hashed_refresh,
            ex=settings.REFRESH_TOKEN_EXPIRE_SECONDS,
        )

        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
        }

    async def logout(
        self,
        payload: RefreshRequest,
    ):
        """Выполняет операцию logout."""
        payload = decode_token(payload.refresh_token)
        user_id = payload["sub"]
        user = await self.user_repo.get_by_id(UUID(user_id))
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found",
            )
        if payload["tv"] != user.token_version:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token revoked",
            )

        if payload["type"] != "refresh":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token",
            )

        token_version = payload["tv"]
        if token_version != user.token_version:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token",
            )

        jti = payload["jti"]
        deleted = await self.redis.delete(f"refresh:{user_id}:{jti}")

        if not deleted:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token already revoked",
            )

    async def refresh_tokens(
        self,
        payload_data: RefreshRequest,
    ):
        """Выполняет операцию refresh tokens."""
        try:
            payload = decode_token(payload_data.refresh_token)

        except JWTError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token",
            ) from None

        if payload["type"] != "refresh":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token type",
            )
        user_id = payload["sub"]
        jti = payload["jti"]
        refresh_key = f"refresh:{user_id}:{jti}"

        stored_hash: str | None = await self.redis.get(refresh_key)

        if not stored_hash:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token revoked",
            )

        if not verify_password(
            payload_data.refresh_token,
            stored_hash,
        ):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token",
            )
        user = await self.user_repo.get_by_id(UUID(user_id))
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found",
            )
        if payload["tv"] != user.token_version:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token revoked",
            )

        consumed = await cast(RefreshTokenRedis, self.redis).eval(
            CONSUME_REFRESH_TOKEN_SCRIPT,
            1,
            refresh_key,
            stored_hash,
        )

        if not consumed:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token revoked",
            )

        access_token = create_access_token(
            user_id,
            user.token_version,
        )

        new_refresh_token, new_jti = create_refresh_token(
            user_id,
            user.token_version,
        )

        await self.redis.set(
            f"refresh:{user_id}:{new_jti}",
            hash_token(new_refresh_token),
            ex=settings.REFRESH_TOKEN_EXPIRE_SECONDS,
        )

        return {
            "access_token": access_token,
            "refresh_token": new_refresh_token,
        }

    async def fake_auth(
        self,
        email: str,
        password: str,
    ):
        """Выполняет операцию fake auth."""
        if await self.user_repo.get_by_email(email):
            return await self.login(
                email,
                password,
            )

        await self.register(
            email,
            password,
        )

        return await self.login(
            email,
            password,
        )
