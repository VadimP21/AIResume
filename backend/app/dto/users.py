"""Содержит DTO, относящиеся к пользователям и аутентификации."""

from dataclasses import dataclass
from uuid import UUID


@dataclass(frozen=True, slots=True)
class CreateUserCommand:
    """Содержит данные для создания пользователя."""

    email: str
    password: str


@dataclass(frozen=True, slots=True)
class UserDTO:
    """Содержит безопасные данные пользователя."""

    id: UUID
    email: str
    is_active: bool
    token_version: int


@dataclass(frozen=True, slots=True)
class UserAuthDTO:
    """Содержит данные пользователя, необходимые аутентификации."""

    id: UUID
    email: str
    password_hash: str
    is_active: bool
    token_version: int
