from fastapi import APIRouter

from app.api.v1.auth.router import router as auth_router
from app.api.v1.users.router import router as users_router
from app.api.v1.health.router import router as health_router
# from app.api.v1.resumes.router import router as resumes_router

api_router = APIRouter(prefix="/api/v1")

api_router.include_router(auth_router)
api_router.include_router(users_router)
api_router.include_router(health_router)
# api_router.include_router(resumes_router)