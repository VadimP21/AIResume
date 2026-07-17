"""Содержит адаптеры Gemini, DeepSeek и GigaChat для импорта резюме."""

import asyncio
from collections.abc import Callable
from time import time
from typing import Any
from uuid import uuid4

import httpx
from openai import (
    APIConnectionError,
    APIStatusError,
    APITimeoutError,
    AsyncOpenAI,
    AuthenticationError,
    OpenAIError,
)

from app.services.ai.exceptions import AIErrorCategory, AIProviderError

GEMINI_BASE_URL = "https://generativelanguage.googleapis.com/v1beta"
GIGACHAT_OAUTH_URL = "https://ngw.devices.sberbank.ru:9443/api/v2/oauth"
RESUME_RESPONSE_SCHEMA = {
    "type": "object",
    "properties": {
        "title": {"type": "string"},
        "sections": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "section_type": {"type": "string"},
                    "content": {"type": "object"},
                },
                "required": ["section_type", "content"],
            },
        },
    },
    "required": ["title", "sections"],
}


class GeminiAIClient:
    """Запрашивает структурированный JSON через нативный Gemini REST API."""

    provider = "gemini"

    def __init__(
        self,
        api_key: str,
        model: str,
        timeout_seconds: float,
        transport: httpx.AsyncBaseTransport | None = None,
    ) -> None:
        """Инициализирует Gemini-клиент."""
        self.api_key = api_key
        self.model = model
        self.timeout_seconds = timeout_seconds
        self.transport = transport

    async def generate_json(self, system_prompt: str, text: str) -> str:
        """Возвращает структурированный JSON из Gemini."""
        payload = {
            "systemInstruction": {"parts": [{"text": system_prompt}]},
            "contents": [{"role": "user", "parts": [{"text": text}]}],
            "generationConfig": {
                "responseMimeType": "application/json",
                "responseJsonSchema": RESUME_RESPONSE_SCHEMA,
            },
        }
        try:
            async with httpx.AsyncClient(
                timeout=self.timeout_seconds,
                transport=self.transport,
            ) as client:
                response = await client.post(
                    f"{GEMINI_BASE_URL}/models/{self.model}:generateContent",
                    headers={"x-goog-api-key": self.api_key},
                    json=payload,
                )
                self._raise_for_status(response)
                data = response.json()
        except httpx.TimeoutException as exc:
            raise AIProviderError("timeout") from exc
        except httpx.RequestError as exc:
            raise AIProviderError("unavailable") from exc
        return _extract_gemini_content(data)

    @staticmethod
    def _raise_for_status(response: httpx.Response) -> None:
        """Преобразует HTTP-ошибку Gemini в безопасную категорию."""
        if response.is_success:
            return
        if response.status_code in {401, 403}:
            raise AIProviderError("authentication")
        raise AIProviderError("unavailable")


class DeepSeekAIClient:
    """Запрашивает JSON через OpenAI-совместимый API DeepSeek."""

    provider = "deepseek"

    def __init__(
        self,
        api_key: str,
        model: str,
        base_url: str,
        timeout_seconds: float,
        client_factory: Callable[..., Any] = AsyncOpenAI,
    ) -> None:
        """Инициализирует DeepSeek-клиент."""
        self.api_key = api_key
        self.model = model
        self.base_url = base_url
        self.timeout_seconds = timeout_seconds
        self.client_factory = client_factory

    async def generate_json(self, system_prompt: str, text: str) -> str:
        """Возвращает JSON из DeepSeek."""
        client = self.client_factory(
            api_key=self.api_key,
            base_url=self.base_url,
            timeout=self.timeout_seconds,
        )
        try:
            completion = await client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": text},
                ],
                response_format={"type": "json_object"},
            )
            return _extract_openai_content(completion)
        except APITimeoutError as exc:
            raise AIProviderError("timeout") from exc
        except (AuthenticationError, APIConnectionError) as exc:
            if isinstance(exc, AuthenticationError):
                raise AIProviderError("authentication") from exc
            raise AIProviderError("unavailable") from exc
        except APIStatusError as exc:
            raise AIProviderError(_status_error_category(exc.status_code)) from exc
        except OpenAIError as exc:
            raise AIProviderError("unavailable") from exc
        finally:
            await client.close()


class GigaChatAIClient:
    """Запрашивает JSON через GigaChat с OAuth-кэшем access token."""

    provider = "gigachat"

    def __init__(
        self,
        auth_key: str,
        model: str,
        base_url: str,
        timeout_seconds: float,
        transport: httpx.AsyncBaseTransport | None = None,
        time_provider: Callable[[], float] = time,
    ) -> None:
        """Инициализирует GigaChat-клиент."""
        self.auth_key = auth_key
        self.model = model
        self.base_url = base_url.rstrip("/")
        self.timeout_seconds = timeout_seconds
        self.transport = transport
        self.time_provider = time_provider
        self._access_token: str | None = None
        self._expires_at = 0.0
        self._token_lock = asyncio.Lock()

    async def generate_json(self, system_prompt: str, text: str) -> str:
        """Возвращает JSON из GigaChat."""
        token = await self._get_access_token()
        try:
            async with self._http_client() as client:
                response = await client.post(
                    f"{self.base_url}/chat/completions",
                    headers={"Authorization": f"Bearer {token}"},
                    json={
                        "model": self.model,
                        "messages": [
                            {"role": "system", "content": system_prompt},
                            {"role": "user", "content": text},
                        ],
                        "response_format": {"type": "json_object"},
                    },
                )
                self._raise_for_status(response)
                data = response.json()
        except httpx.TimeoutException as exc:
            raise AIProviderError("timeout") from exc
        except httpx.RequestError as exc:
            raise AIProviderError("unavailable") from exc
        return _extract_openai_content(data)

    async def _get_access_token(self) -> str:
        """Возвращает действующий OAuth-токен или безопасно обновляет его."""
        if self._has_valid_token():
            return self._access_token or ""

        async with self._token_lock:
            if self._has_valid_token():
                return self._access_token or ""
            await self._refresh_access_token()
            return self._access_token or ""

    def _has_valid_token(self) -> bool:
        """Проверяет, что OAuth-токен ещё действителен."""
        return (
            self._access_token is not None
            and self._expires_at > self.time_provider() + 5
        )

    async def _refresh_access_token(self) -> None:
        """Получает и сохраняет новый OAuth-токен GigaChat."""
        try:
            async with self._http_client() as client:
                response = await client.post(
                    GIGACHAT_OAUTH_URL,
                    headers={
                        "Accept": "application/json",
                        "Authorization": f"Basic {self.auth_key}",
                        "RqUID": str(uuid4()),
                    },
                    data={"scope": "GIGACHAT_API_PERS"},
                )
                self._raise_for_status(response)
                data = response.json()
        except httpx.TimeoutException as exc:
            raise AIProviderError("timeout") from exc
        except httpx.RequestError as exc:
            raise AIProviderError("unavailable") from exc

        token = data.get("access_token")
        expires_at = data.get("expires_at")
        if (
            not isinstance(token, str)
            or not token
            or not isinstance(expires_at, (int, float))
        ):
            raise AIProviderError("unavailable")
        self._access_token = token
        self._expires_at = float(expires_at)

    def _http_client(self) -> httpx.AsyncClient:
        """Создаёт краткоживущий HTTP-клиент с заданным таймаутом."""
        return httpx.AsyncClient(
            timeout=self.timeout_seconds,
            transport=self.transport,
        )

    @staticmethod
    def _raise_for_status(response: httpx.Response) -> None:
        """Преобразует HTTP-ошибку GigaChat в безопасную категорию."""
        if response.is_success:
            return
        if response.status_code in {401, 403}:
            raise AIProviderError("authentication")
        raise AIProviderError("unavailable")


def _extract_gemini_content(data: Any) -> str:
    """Извлекает текст из ответа Gemini или возвращает пустую строку."""
    try:
        content = data["candidates"][0]["content"]["parts"][0]["text"]
    except (IndexError, KeyError, TypeError):
        return ""
    return content if isinstance(content, str) else ""


def _status_error_category(status_code: int) -> AIErrorCategory:
    """Возвращает безопасную категорию HTTP-ошибки провайдера."""
    if status_code in {401, 403}:
        return "authentication"
    return "unavailable"


def _extract_openai_content(data: Any) -> str:
    """Извлекает текст из OpenAI-совместимого ответа или возвращает пустую строку."""
    try:
        choices = data["choices"] if isinstance(data, dict) else data.choices
        content = (
            choices[0]["message"]["content"]
            if isinstance(choices[0], dict)
            else choices[0].message.content
        )
    except (AttributeError, IndexError, KeyError, TypeError):
        return ""
    return content if isinstance(content, str) else ""
