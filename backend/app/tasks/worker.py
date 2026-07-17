"""Содержит компоненты модуля worker."""

from celery import Celery

from app.core.config import settings

celery_app = Celery(
    "worker",
    broker=str(settings.REDIS_URL),
    backend=str(settings.REDIS_URL),
)


@celery_app.task
def ping() -> str:
    """Выполняет операцию ping."""
    return "pong"
