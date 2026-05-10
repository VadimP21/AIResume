from fastapi import APIRouter
from sqlalchemy import text

from app.db.redis import redis_client
from app.db.session import AsyncSessionLocal


router = APIRouter(
    prefix="/health",
    tags=["health"],
)


@router.get("")
async def healthcheck():
    db_status = "ok"
    redis_status = "ok"
    
    try:
        async with AsyncSessionLocal() as session:
            await session.execute(text("SELECT 1"))
    except Exception:
        redis_status = "error"

    try:
        await redis_client.ping()
    except Exception:
        redis_status = "error"

    return {
        "status": "ok",
        "database": db_status,
        "redis": redis_status,
    }