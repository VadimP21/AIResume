"""Содержит компоненты модуля security."""

from datetime import UTC, datetime, timedelta
from typing import Any
from uuid import uuid4

import jwt
from fastapi import HTTPException
from jwt import ExpiredSignatureError, InvalidTokenError
from passlib.context import CryptContext
from starlette import status

from app.core.config import settings

pwd_context = CryptContext(
    schemes=["argon2"],
    argon2__memory_cost=65536,
    argon2__time_cost=3,
    argon2__parallelism=4,
)


def hash_password(password: str) -> str:
    """
    Хеширует пароль пользователя с использованием Argon2.

    Используется перед сохранением пароля в базе данных.
    Открытый пароль никогда не должен храниться в БД.
    """
    return pwd_context.hash(password)


def verify_password(
    plain_password: str,
    hashed_password: str,
) -> bool:
    """
    Проверяет соответствие пароля и его хеша.

    Используется при аутентификации пользователя.
    """
    return pwd_context.verify(
        plain_password,
        hashed_password,
    )


def hash_token(token: str) -> str:
    """
    Хеширует refresh token перед сохранением в Redis.

    Позволяет не хранить токены в открытом виде.
    """
    return pwd_context.hash(token)


def create_access_token(
    subject: str,
    token_version: int,
) -> str:
    """
    Создает JWT access token.

    Access token используется для доступа к защищенным endpoint API.
    Токен содержит идентификатор пользователя, срок действия,
    issuer, audience и версию токена.
    """
    expire = datetime.now(UTC) + timedelta(
        minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES
    )
    now = datetime.now(UTC)
    payload: dict[str, Any] = {
        "sub": subject,
        "exp": expire,
        "iat": now,
        "type": "access",
        "iss": settings.JWT_ISSUER,
        "aud": settings.JWT_AUDIENCE,
        "tv": token_version,
    }
    return jwt.encode(
        payload,
        settings.JWT_SECRET,
        algorithm=settings.JWT_ALGORITHM,
    )


def create_refresh_token(
    subject: str,
    token_version: int,
) -> tuple[str, str]:
    """
    Создает JWT refresh token и его уникальный идентификатор.

    Refresh token используется для получения новых access token
    без повторной авторизации пользователя.

    Возвращает:
        tuple[token, jti]
    """
    expire = datetime.now(UTC) + timedelta(days=7)
    now = datetime.now(UTC)
    jti = str(uuid4())
    payload = {
        "sub": subject,
        "exp": expire,
        "iat": now,
        "type": "refresh",
        "jti": jti,
        "iss": settings.JWT_ISSUER,
        "aud": settings.JWT_AUDIENCE,
        "tv": token_version,
    }
    token = jwt.encode(
        payload,
        settings.JWT_SECRET,
        algorithm=settings.JWT_ALGORITHM,
    )
    return token, jti


def decode_token(token: str) -> dict[str, Any]:
    """
    Декодирует и валидирует JWT token.

    Проверяет:
    - подпись токена
    - срок действия
    - issuer
    - audience

    Вызывает HTTPException при невалидном или истекшем токене.
    """
    try:
        payload = jwt.decode(
            token,
            settings.JWT_SECRET,
            algorithms=[settings.JWT_ALGORITHM],
            issuer=settings.JWT_ISSUER,
            audience=settings.JWT_AUDIENCE,
        )
    except ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Token expired"
        ) from None
    except InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token"
        ) from None
    return payload
