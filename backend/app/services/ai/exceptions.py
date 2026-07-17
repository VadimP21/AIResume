"""Содержит внутренние ошибки интеграции с AI-провайдерами."""

from typing import Literal

AIErrorCategory = Literal[
    "authentication",
    "configuration",
    "timeout",
    "unavailable",
]


class AIProviderError(Exception):
    """Описывает безопасную категорию ошибки запроса к провайдеру."""

    def __init__(self, category: AIErrorCategory):
        """Инициализирует ошибку безопасной категорией."""
        self.category = category
        super().__init__(category)


class AIConfigurationError(Exception):
    """Описывает отсутствие обязательной конфигурации провайдера."""

    def __init__(self, provider: str):
        """Инициализирует ошибку именем провайдера."""
        self.provider = provider
        super().__init__(provider)
