from __future__ import annotations

import json
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Protocol

import httpx

from .utils import read_yaml


@dataclass(frozen=True)
class ProviderResponse:
    text: str
    latency_seconds: float
    token_usage: dict[str, int] | None = None
    model_id: str = "unknown"
    provider: str = "unknown"


class LLMProvider(Protocol):
    provider_name: str
    model_id: str

    def complete(self, prompt: str, snippet: str) -> ProviderResponse:
        """Return one model response for a prompt and snippet."""


class MockProvider:
    provider_name = "mock"
    model_id = "mock-evidence-grounded-v1"

    def __init__(self, fixture_path: Path = Path("gold/gold_standard.yaml")) -> None:
        self.fixture_path = fixture_path

    def complete(self, prompt: str, snippet: str) -> ProviderResponse:
        start = time.perf_counter()
        gold = read_yaml(self.fixture_path)
        source = next(item for item in gold["sources"] if item["text"] == snippet)
        payload: dict[str, Any] = {
            "source": {"id": source["id"], "label": source["label"]},
            "parameters": [],
        }
        for parameter in source["parameters"]:
            copied = {
                key: value for key, value in parameter.items() if key != "annotation_reasoning"
            }
            payload["parameters"].append(copied)
        text = json.dumps(payload, indent=2)
        return ProviderResponse(
            text=text,
            latency_seconds=time.perf_counter() - start,
            token_usage=None,
            model_id=self.model_id,
            provider=self.provider_name,
        )


class OpenAIResponsesProvider:
    provider_name = "openai"

    def __init__(
        self,
        api_key: str,
        model_id: str = "gpt-4.1-mini",
        temperature: float = 0.0,
        max_output_tokens: int = 2000,
    ) -> None:
        self.api_key = api_key
        self.model_id = model_id
        self.temperature = temperature
        self.max_output_tokens = max_output_tokens

    def complete(self, prompt: str, snippet: str) -> ProviderResponse:
        start = time.perf_counter()
        payload = {
            "model": self.model_id,
            "input": prompt,
            "temperature": self.temperature,
            "max_output_tokens": self.max_output_tokens,
            "text": {"format": {"type": "json_object"}},
        }
        response = httpx.post(
            "https://api.openai.com/v1/responses",
            headers={"Authorization": f"Bearer {self.api_key}"},
            json=payload,
            timeout=60,
        )
        response.raise_for_status()
        data = response.json()
        text = data.get("output_text")
        if not isinstance(text, str):
            fragments: list[str] = []
            for item in data.get("output", []):
                for content in item.get("content", []):
                    if content.get("type") in {"output_text", "text"}:
                        fragments.append(str(content.get("text", "")))
            text = "".join(fragments)
        usage = data.get("usage")
        token_usage = usage if isinstance(usage, dict) else None
        return ProviderResponse(
            text=text,
            latency_seconds=time.perf_counter() - start,
            token_usage=token_usage,
            model_id=self.model_id,
            provider=self.provider_name,
        )


class DeepSeekChatProvider:
    provider_name = "deepseek"

    def __init__(
        self,
        api_key: str,
        model_id: str = "deepseek-v4-pro",
        temperature: float = 0.0,
        max_tokens: int = 2000,
    ) -> None:
        self.api_key = api_key
        self.model_id = model_id
        self.temperature = temperature
        self.max_tokens = max_tokens

    def complete(self, prompt: str, snippet: str) -> ProviderResponse:
        start = time.perf_counter()
        payload = {
            "model": self.model_id,
            "messages": [
                {"role": "system", "content": prompt},
                {
                    "role": "user",
                    "content": "Return only the JSON object for the supplied snippet.",
                },
            ],
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
            "thinking": {"type": "disabled"},
            "response_format": {"type": "json_object"},
        }
        response = httpx.post(
            "https://api.deepseek.com/chat/completions",
            headers={"Authorization": f"Bearer {self.api_key}"},
            json=payload,
            timeout=60,
        )
        response.raise_for_status()
        data = response.json()
        choices = data.get("choices", [])
        text = ""
        if choices:
            message = choices[0].get("message", {})
            content = message.get("content", "")
            if isinstance(content, str):
                text = content
        usage = data.get("usage")
        token_usage = usage if isinstance(usage, dict) else None
        return ProviderResponse(
            text=text,
            latency_seconds=time.perf_counter() - start,
            token_usage=token_usage,
            model_id=self.model_id,
            provider=self.provider_name,
        )
