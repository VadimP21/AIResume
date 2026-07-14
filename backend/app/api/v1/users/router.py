"""Содержит компоненты модуля router."""

from fastapi import APIRouter, Depends

from app.api.v1.auth.dependencies import get_current_user
from app.api.v1.auth.schemas import UserResponse
from app.models.user import User

router = APIRouter(
    prefix="/users",
    tags=["users"],
)


@router.get(
    "/me",
    response_model=UserResponse,
)
async def me(
    user: User = Depends(get_current_user),
):
    """Выполняет операцию me."""
    return user
