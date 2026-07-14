"""Преобразует текст резюме в поддерживаемые секции через OpenAI."""

from typing import Any

from pydantic import ValidationError

from app.core.exceptions import ValidationException
from app.schemas.resume_import import ImportedResumeSchema


class ResumeAIParser:
    """Запрашивает у OpenAI структурированное резюме."""

    def __init__(self, client: Any, model: str) -> None:
        """Инициализирует экземпляр."""
        self.client = client
        self.model = model

    async def parse(self, text: str) -> ImportedResumeSchema:
        """Извлекает структуру резюме из текста."""
        try:
            completion = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "Extract a resume into title and only summary, experience, "
                            "skills sections. Return JSON matching the provided schema."
                        ),
                    },
                    {"role": "user", "content": text},
                ],
                response_format={"type": "json_object"},
            )
            content = completion.choices[0].message.content
            if content is None:
                raise ValidationException("AI response is invalid")
            return ImportedResumeSchema.model_validate_json(content)
        except ValidationException:
            raise
        except (IndexError, ValidationError, ValueError) as exc:
            raise ValidationException("AI response is invalid") from exc
        except Exception as exc:
            raise ValidationException("Unable to parse resume") from exc
