"""Содержит компоненты модуля user_repository."""

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.dto.users import UserAuthDTO, UserDTO
from app.models.user import User
from app.repositories.mappers.users import user_to_auth_dto, user_to_dto


class UserRepository:
    """Представляет сущность UserRepository."""

    def __init__(self, session: AsyncSession):
        """Инициализирует экземпляр."""
        self.session = session

    async def get_by_id(
        self,
        user_id: UUID,
    ) -> UserAuthDTO | None:
        """Возвращает by id."""
        stmt = select(User).where(User.id == user_id)

        result = await self.session.execute(stmt)

        user = result.scalar_one_or_none()
        return user_to_auth_dto(user) if user is not None else None

    async def get_by_email(
        self,
        email: str,
    ) -> UserAuthDTO | None:
        """Возвращает by email."""
        stmt = select(User).where(User.email == email)

        result = await self.session.execute(stmt)

        user = result.scalar_one_or_none()
        return user_to_auth_dto(user) if user is not None else None

    async def create(
        self,
        *,
        email: str,
        hashed_password: str,
    ) -> UserDTO:
        """Выполняет операцию create."""
        user = User(
            email=email,
            hashed_password=hashed_password,
        )

        self.session.add(user)

        await self.session.flush()
        await self.session.refresh(user)

        return user_to_dto(user)
