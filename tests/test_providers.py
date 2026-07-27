from __future__ import annotations

import pytest

from riscv_parameter_extractor.models import Snippet
from riscv_parameter_extractor.providers import DeepSeekChatProvider, MockProvider
from riscv_parameter_extractor.validation import validate_response


def test_mock_provider_success(snippets: list[dict[str, str]]) -> None:
    snippet = Snippet.model_validate(snippets[0])
    response = MockProvider().complete("prompt", snippet.text)
    result, report = validate_response(response.text, snippet.text)
    assert report.ok
    assert result is not None


def test_mock_provider_invalid_json_path(snippets: list[dict[str, str]]) -> None:
    _snippet = Snippet.model_validate(snippets[0])
    result, report = validate_response("not json", "snippet")
    assert result is None
    assert not report.ok


def test_mock_provider_timeout_shape() -> None:
    class TimeoutProvider:
        def complete(self, prompt: str, snippet: str) -> str:
            raise TimeoutError("timed out")

    provider = TimeoutProvider()
    with pytest.raises(TimeoutError):
        provider.complete("prompt", "snippet")


def test_deepseek_provider_uses_chat_completions(monkeypatch) -> None:
    captured = {}

    class FakeResponse:
        def raise_for_status(self) -> None:
            return None

        def json(self) -> dict:
            return {
                "choices": [{"message": {"content": '{"parameters": []}'}}],
                "usage": {"prompt_tokens": 3, "completion_tokens": 4, "total_tokens": 7},
            }

    def fake_post(url: str, headers: dict, json: dict, timeout: int) -> FakeResponse:
        captured["url"] = url
        captured["headers"] = headers
        captured["json"] = json
        captured["timeout"] = timeout
        return FakeResponse()

    monkeypatch.setattr("riscv_parameter_extractor.providers.httpx.post", fake_post)

    response = DeepSeekChatProvider(api_key="test-key").complete("Return json.", "snippet")

    assert captured["url"] == "https://api.deepseek.com/chat/completions"
    assert captured["headers"]["Authorization"] == "Bearer test-key"
    assert captured["json"]["model"] == "deepseek-v4-pro"
    assert captured["json"]["thinking"] == {"type": "disabled"}
    assert captured["json"]["response_format"] == {"type": "json_object"}
    assert response.text == '{"parameters": []}'
    assert response.provider == "deepseek"
    assert response.token_usage == {"prompt_tokens": 3, "completion_tokens": 4, "total_tokens": 7}
