"""Тестирует клиентов внешних AI-провайдеров."""

import asyncio
import json

import httpx
import pytest

from app.services.ai.clients import (
    DeepSeekAIClient,
    GeminiAIClient,
    GigaChatAIClient,
)
from app.services.ai.exceptions import AIProviderError


def json_response() -> str:
    """Возвращает корректный JSON ответа модели."""
    return (
        '{"title":"Developer","sections":['
        '{"section_type":"summary","content":{"text":"Backend"}}]}'
    )


@pytest.mark.asyncio
async def test_gemini_requests_structured_json() -> None:
    """Отправляет Gemini запрос с JSON-форматом и возвращает текст ответа."""
    requests: list[httpx.Request] = []

    def handler(request: httpx.Request) -> httpx.Response:
        """Имитирует успешный ответ Gemini."""
        requests.append(request)
        return httpx.Response(
            200,
            json={"candidates": [{"content": {"parts": [{"text": json_response()}]}}]},
        )

    client = GeminiAIClient(
        api_key="gemini-key",
        model="gemini-test",
        timeout_seconds=1,
        transport=httpx.MockTransport(handler),
    )

    result = await client.generate_json("system prompt", "resume text")

    assert result == json_response()
    assert requests[0].url.path.endswith("/models/gemini-test:generateContent")
    assert requests[0].headers["x-goog-api-key"] == "gemini-key"
    assert json.loads(requests[0].content)["generationConfig"]["responseMimeType"] == (
        "application/json"
    )


@pytest.mark.asyncio
async def test_deepseek_returns_completion_content() -> None:
    """Извлекает JSON из OpenAI-совместимого ответа DeepSeek."""
    message = type("Message", (), {"content": json_response()})()
    completion = type(
        "Completion",
        (),
        {
            "choices": [
                type(
                    "Choice",
                    (),
                    {"message": message},
                )()
            ]
        },
    )()
    sdk_client = type(
        "Client",
        (),
        {
            "chat": type(
                "Chat",
                (),
                {
                    "completions": type(
                        "Completions",
                        (),
                        {
                            "create": staticmethod(
                                lambda **_: asyncio.sleep(0, result=completion)
                            )
                        },
                    )()
                },
            )(),
            "close": staticmethod(lambda: asyncio.sleep(0)),
        },
    )()

    client = DeepSeekAIClient(
        api_key="deepseek-key",
        model="deepseek-test",
        base_url="https://example.test/v1",
        timeout_seconds=1,
        client_factory=lambda **_: sdk_client,
    )

    assert await client.generate_json("system prompt", "resume text") == json_response()


@pytest.mark.asyncio
async def test_gigachat_reuses_unexpired_access_token() -> None:
    """Повторно использует действующий access token GigaChat."""
    request_paths: list[str] = []

    def handler(request: httpx.Request) -> httpx.Response:
        """Имитирует OAuth и Chat Completions GigaChat."""
        request_paths.append(request.url.path)
        if request.url.path == "/api/v2/oauth":
            return httpx.Response(
                200,
                json={"access_token": "token-1", "expires_at": 1_000},
            )
        return httpx.Response(
            200,
            json={"choices": [{"message": {"content": json_response()}}]},
        )

    client = GigaChatAIClient(
        auth_key="gigachat-key",
        model="GigaChat-Test",
        base_url="https://giga.example/api/v1",
        timeout_seconds=1,
        transport=httpx.MockTransport(handler),
        time_provider=lambda: 100,
    )

    await client.generate_json("system prompt", "resume text")
    await client.generate_json("system prompt", "resume text")

    assert request_paths.count("/api/v2/oauth") == 1
    assert request_paths.count("/api/v1/chat/completions") == 2


@pytest.mark.asyncio
async def test_gigachat_refreshes_expired_token_once_for_parallel_requests() -> None:
    """Защищает обновление истёкшего токена GigaChat от конкурентных запросов."""
    oauth_calls = 0
    current_time = 100

    def handler(request: httpx.Request) -> httpx.Response:
        """Имитирует обновление OAuth-токена и ответы модели."""
        nonlocal oauth_calls
        if request.url.path == "/api/v2/oauth":
            oauth_calls += 1
            return httpx.Response(
                200,
                json={
                    "access_token": f"token-{oauth_calls}",
                    "expires_at": current_time + 100,
                },
            )
        return httpx.Response(
            200,
            json={"choices": [{"message": {"content": json_response()}}]},
        )

    client = GigaChatAIClient(
        auth_key="gigachat-key",
        model="GigaChat-Test",
        base_url="https://giga.example/api/v1",
        timeout_seconds=1,
        transport=httpx.MockTransport(handler),
        time_provider=lambda: current_time,
    )
    await client.generate_json("system prompt", "resume text")
    current_time = 201

    await asyncio.gather(
        client.generate_json("system prompt", "resume one"),
        client.generate_json("system prompt", "resume two"),
    )

    assert oauth_calls == 2


@pytest.mark.asyncio
async def test_provider_maps_authentication_failure_to_safe_category() -> None:
    """Не раскрывает ответ провайдера при ошибке авторизации."""
    transport = httpx.MockTransport(
        lambda request: httpx.Response(401, text="credential must stay secret")
    )
    client = GeminiAIClient(
        api_key="gemini-key",
        model="gemini-test",
        timeout_seconds=1,
        transport=transport,
    )

    with pytest.raises(AIProviderError, match="authentication") as exc_info:
        await client.generate_json("system prompt", "resume text")

    assert exc_info.value.category == "authentication"


@pytest.mark.asyncio
async def test_provider_maps_server_failure_to_safe_category() -> None:
    """Относит HTTP 5xx провайдера к безопасной категории unavailable."""
    transport = httpx.MockTransport(
        lambda request: httpx.Response(503, text="internal provider error")
    )
    client = GeminiAIClient(
        api_key="gemini-key",
        model="gemini-test",
        timeout_seconds=1,
        transport=transport,
    )

    with pytest.raises(AIProviderError, match="unavailable"):
        await client.generate_json("system prompt", "resume text")


@pytest.mark.asyncio
async def test_provider_maps_timeout_to_safe_category() -> None:
    """Относит таймаут провайдера к безопасной категории timeout."""
    transport = httpx.MockTransport(
        lambda request: (_ for _ in ()).throw(httpx.ReadTimeout("timeout"))
    )
    client = GeminiAIClient(
        api_key="gemini-key",
        model="gemini-test",
        timeout_seconds=1,
        transport=transport,
    )

    with pytest.raises(AIProviderError, match="timeout"):
        await client.generate_json("system prompt", "resume text")
