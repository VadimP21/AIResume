from typing import Annotated

from fastapi import APIRouter, Depends

from app.api.v1.auth.dependencies import get_auth_service
from app.api.v1.auth.schemas import (
    RegisterRequest,
    LoginRequest,
    TokenResponse, UserResponse, RefreshRequest,
)
from app.services.auth_service import AuthService

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register",
             response_model=UserResponse,
             )
async def register(
        payload: RegisterRequest,
        service: Annotated[
            AuthService,
            Depends(get_auth_service),
        ]):
    user = await service.register(
        payload.email,
        payload.password,
    )
    return user


@router.post(
    "/login",
    response_model=TokenResponse,
)
async def login(
        payload: LoginRequest,
        service: Annotated[
            AuthService,
            Depends(get_auth_service),
        ]):
    return await service.login(
        payload.email,
        payload.password,
    )


@router.post("/logout")
async def logout(
        payload: RefreshRequest,
        service: Annotated[
            AuthService,
            Depends(get_auth_service),
        ]):
    await service.logout(payload)

    return {"message": "Logged out"}


@router.post(
    "/refresh",
    response_model=TokenResponse,
)
async def refresh(
        payload: RefreshRequest,
        service: Annotated[
            AuthService,
            Depends(get_auth_service),
        ]):
    return await service.refresh_tokens(payload)
