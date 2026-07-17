"""Определяет контракт клиента AI-провайдера."""

from typing import Protocol


class ResumeAIClient(Protocol):
    """Определяет получение JSON для импорта резюме."""

    provider: str
    model: str

    async def generate_json(self, system_prompt: str, text: str) -> str:
        """Возвращает JSON-ответ модели для текста резюме."""
