from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

KNOWN_PROVIDER_KEYS = {
    "openai": "OPENAI_API_KEY",
    "anthropic": "ANTHROPIC_API_KEY",
    "deepseek": "DEEPSEEK_API_KEY",
    "gemini": "GEMINI_API_KEY",
    "google": "GOOGLE_API_KEY",
    "groq": "GROQ_API_KEY",
    "openrouter": "OPENROUTER_API_KEY",
}


@dataclass(frozen=True)
class AvailableProvider:
    provider: str
    env_var: str
    present: bool


def available_providers() -> list[AvailableProvider]:
    return [
        AvailableProvider(provider=name, env_var=env_var, present=bool(os.getenv(env_var)))
        for name, env_var in KNOWN_PROVIDER_KEYS.items()
    ]


def first_available_provider() -> str | None:
    for provider in available_providers():
        if provider.present:
            return provider.provider
    return None


def load_env_file(path: Path = Path(".env")) -> None:
    """Load simple KEY=VALUE pairs without overriding the process environment."""
    if not path.exists():
        return

    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip("'\"")
        if key and key not in os.environ:
            os.environ[key] = value
