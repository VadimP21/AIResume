"""Содержит компоненты модуля schemas."""

import re
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator


class RegisterRequest(BaseModel):
    """Представляет сущность RegisterRequest."""

    email: EmailStr
    password: str = Field(min_length=8, max_length=128)

    @field_validator("password")
    @classmethod
    def validate_password(
        cls,
        value: str,
    ) -> str:
        """Проверяет password."""
        if len(value) < 8:
            raise ValueError("Password too short")

        if not re.search(r"[A-Z]", value):
            raise ValueError("Password must contain uppercase letter")

        if not re.search(r"[a-z]", value):
            raise ValueError("Password must contain lowercase letter")

        if not re.search(r"\d", value):
            raise ValueError("Password must contain digit")
        if not re.search(
            r"[!@#$%^&*()_\-+=<>?/{}[\]|]",
            value,
        ):
            raise ValueError("Password must contain special character")
        return value


class LoginRequest(BaseModel):
    """Представляет сущность LoginRequest."""

    email: EmailStr
    password: str = Field(min_length=8, max_length=128)


class TokenResponse(BaseModel):
    """Представляет сущность TokenResponse."""

    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class RefreshRequest(BaseModel):
    """Представляет сущность RefreshRequest."""

    refresh_token: str


class UserResponse(BaseModel):
    """Представляет сущность UserResponse."""

    id: UUID
    email: EmailStr

    model_config = ConfigDict(from_attributes=True)
