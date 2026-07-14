"""Содержит компоненты модуля router."""

from fastapi import APIRouter, status
from fastapi.responses import JSONResponse
from sqlalchemy import text

from app.db.redis import redis_client
from app.db.session import AsyncSessionLocal

router = APIRouter(
    prefix="/health",
    tags=["health"],
)


@router.get("")
async def healthcheck():
    """Выполняет операцию healthcheck."""
    db_status = "ok"
    redis_status = "ok"
    try:
        async with AsyncSessionLocal() as session:
            await session.execute(text("SELECT 1"))
    except Exception:
        db_status = "error"

    try:
        await redis_client.ping()
    except Exception:
        redis_status = "error"

    response_status = "ok" if db_status == redis_status == "ok" else "error"
    response = {
        "status": response_status,
        "database": db_status,
        "redis": redis_status,
    }
    if response_status == "error":
        return JSONResponse(response, status_code=status.HTTP_503_SERVICE_UNAVAILABLE)
    return response
