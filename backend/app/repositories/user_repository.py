"""Содержит компоненты модуля user_repository."""

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User


class UserRepository:
    """Представляет сущность UserRepository."""

    def __init__(self, session: AsyncSession):
        """Инициализирует экземпляр."""
        self.session = session

    async def get_by_id(
        self,
        user_id: UUID,
    ) -> User | None:
        """Возвращает by id."""
        stmt = select(User).where(User.id == user_id)

        result = await self.session.execute(stmt)

        return result.scalar_one_or_none()

    async def get_by_email(
        self,
        email: str,
    ) -> User | None:
        """Возвращает by email."""
        stmt = select(User).where(User.email == email)

        result = await self.session.execute(stmt)

        return result.scalar_one_or_none()

    async def create(
        self,
        *,
        email: str,
        hashed_password: str,
    ) -> User:
        """Выполняет операцию create."""
        user = User(
            email=email,
            hashed_password=hashed_password,
        )

        self.session.add(user)

        await self.session.flush()
        await self.session.refresh(user)

        return user
