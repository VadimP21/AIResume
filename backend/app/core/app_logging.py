"""Содержит компоненты модуля app_logging."""

import logging

import structlog

"""
import structlog

logger = structlog.get_logger()

logger.info(
    "user_registered",
    user_id=str(user.id),
    email=user.email,
)

{
  "event": "user_registered",
  "user_id": "123",
  "email": "test@test.com",
  "level": "info",
  "timestamp": "2026-05-11T10:00:00Z"
}
"""


def setup_logging() -> None:
    """Выполняет операцию setup logging."""
    structlog.configure(
        processors=[
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.add_log_level,
            structlog.processors.JSONRenderer(),
        ],
        wrapper_class=structlog.make_filtering_bound_logger(logging.INFO),
    )
