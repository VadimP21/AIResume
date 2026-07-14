"""Содержит компоненты модуля user."""

from sqlalchemy import Boolean, Integer, String, text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base
from app.db.mixins import TimestampMixin, UUIDMixin


class User(
    Base,
    UUIDMixin,
    TimestampMixin,
):
    """Представляет сущность User."""

    __tablename__ = "users"

    email: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        nullable=False,
    )

    hashed_password: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        server_default=text("true"),
    )

    token_version: Mapped[int] = mapped_column(
        Integer, nullable=False, server_default=text("1")
    )
