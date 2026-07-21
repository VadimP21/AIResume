"""Содержит мапперы ORM-пользователей во внутренние DTO."""

from app.dto.users import UserAuthDTO, UserDTO
from app.models.user import User


def user_to_dto(user: User) -> UserDTO:
    """Преобразует ORM-пользователя в безопасный DTO."""
    return UserDTO(
        id=user.id,
        email=user.email,
        is_active=user.is_active,
        token_version=user.token_version,
    )


def user_to_auth_dto(user: User) -> UserAuthDTO:
    """Преобразует ORM-пользователя в DTO для аутентификации."""
    return UserAuthDTO(
        id=user.id,
        email=user.email,
        password_hash=user.hashed_password,
        is_active=user.is_active,
        token_version=user.token_version,
    )
