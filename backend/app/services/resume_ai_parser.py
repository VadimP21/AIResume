"""Преобразует текст резюме в структурированные данные через AI-провайдера."""

from time import perf_counter

import structlog
from pydantic import ValidationError

from app.core.exceptions import ServiceUnavailableException, ValidationException
from app.schemas.resume_import import ImportedResumeSchema
from app.services.ai.exceptions import AIProviderError
from app.services.ai.protocols import ResumeAIClient

logger = structlog.get_logger()

RESUME_IMPORT_UNAVAILABLE_MESSAGE = "Resume import is temporarily unavailable"
RESUME_IMPORT_PROMPT = (
    "Extract a resume into a title and only summary, experience, education, skills, "
    "projects, and languages sections. Return a JSON object matching the expected "
    "resume schema. Do not include Markdown or any explanation."
)


class ResumeAIParser:
    """Запрашивает у AI-провайдера структурированное резюме."""

    def __init__(self, client: ResumeAIClient) -> None:
        """Инициализирует парсер клиентом AI-провайдера."""
        self.client = client

    async def parse(self, text: str) -> ImportedResumeSchema:
        """Извлекает и валидирует структуру резюме из текста."""
        started_at = perf_counter()
        try:
            content = await self.client.generate_json(RESUME_IMPORT_PROMPT, text)
            result = ImportedResumeSchema.model_validate_json(content)
            self._log_success(started_at)
            return result
        except AIProviderError as exc:
            self._log_failure(exc.category, started_at)
            raise ServiceUnavailableException(
                RESUME_IMPORT_UNAVAILABLE_MESSAGE
            ) from exc
        except (ValidationError, ValueError) as exc:
            self._log_failure("invalid_response", started_at)
            raise ValidationException("AI response is invalid") from exc
        except Exception as exc:
            self._log_failure("unavailable", started_at)
            raise ServiceUnavailableException(
                RESUME_IMPORT_UNAVAILABLE_MESSAGE
            ) from exc

    def _log_failure(self, error_category: str, started_at: float) -> None:
        """Логирует безопасные метаданные неуспешного AI-запроса."""
        logger.warning(
            "resume_ai_parse_failed",
            provider=self.client.provider,
            model=self.client.model,
            duration_ms=round((perf_counter() - started_at) * 1000),
            error_category=error_category,
        )

    def _log_success(self, started_at: float) -> None:
        """Логирует безопасные метаданные успешного AI-запроса."""
        logger.info(
            "resume_ai_parse_completed",
            provider=self.client.provider,
            model=self.client.model,
            duration_ms=round((perf_counter() - started_at) * 1000),
        )
