from fastapi import HTTPException, status
from jose import JWTError
from redis.asyncio import Redis
from sqlalchemy.exc import IntegrityError

from app.api.v1.auth.schemas import RefreshRequest
from app.core.security import (
    hash_password,
    verify_password,
    create_access_token,
    create_refresh_token, hash_token, decode_token,
)
from app.repositories.user_repository import UserRepository


class AuthService:
    def __init__(
        self,
        user_repo: UserRepository,
        redis: Redis,
    ):
        self.user_repo = user_repo
        self.redis = redis

    async def register(
        self,
        email: str,
        password: str,
    ):
        try:
            email = email.lower().strip()
            print(self.user_repo.session)
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
            )
        except Exception:
            await self.user_repo.session.rollback()
            raise

        return user

    async def login(
        self,
        email: str,
        password: str,
    ):
        email = email.lower().strip()
        user = await self.user_repo.get_by_email(email)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid credentials, user not existing",
            )

        if not user.is_active:
            raise HTTPException(403)

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
            ex=60 * 60 * 24 * 7,
        )

        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
        }

    async def logout(
            self,
            payload: RefreshRequest,
    ):
        payload = decode_token(payload.refresh_token)
        user_id = payload["sub"]
        user = await self.user_repo.get_by_id(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found",
            )

        if payload["type"] != "refresh":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token, type not 'refresh'",
            )

        jti = payload["jti"]

        deleted = await self.redis.delete(
            f"refresh:{user_id}:{jti}"
        )

        if not deleted:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token already revoked",
            )

    async def refresh_tokens(
        self,
            payload_data: RefreshRequest,
    ):
        try:
            payload = decode_token(payload_data.refresh_token)

        except JWTError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token",
            )

        if payload["type"] != "refresh":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token type",
            )
        user_id = payload["sub"]
        jti = payload["jti"]

        stored_hash = await self.redis.get(
            f"refresh:{user_id}:{jti}"
        )

        if not stored_hash:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token revoked",
            )

        if not verify_password(
            payload_data.refresh_token,
            stored_hash.decode(),
        ):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token",
            )

        token_version = payload["tv"]
        access_token = create_access_token(user_id, token_version)

        new_refresh_token, new_jti = create_refresh_token(
            user_id, token_version
        )

        await self.redis.delete(f"refresh:{user_id}:{jti}")

        await self.redis.set(
            f"refresh:{user_id}:{new_jti}",
            hash_token(new_refresh_token),
            ex=60 * 60 * 24 * 7,
        )

        return {
            "access_token": access_token,
            "refresh_token": new_refresh_token,
        }