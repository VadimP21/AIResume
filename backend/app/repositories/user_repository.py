from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User


class UserRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id(
        self,
        user_id: UUID,
    ) -> User | None:
        stmt = select(User).where(User.id == user_id)

        result = await self.session.execute(stmt)

        return result.scalar_one_or_none()

    async def get_by_email(
        self,
        email: str,
    ) -> User | None:
        stmt = select(User).where(User.email == email)

        result = await self.session.execute(stmt)

        return result.scalar_one_or_none()

    async def create(
        self,
        *,
        email: str,
        hashed_password: str,
    ) -> User:
        user = User(
            email=email,
            hashed_password=hashed_password,
        )

        self.session.add(user)

        await self.session.flush()
        await self.session.refresh(user)

        return user
