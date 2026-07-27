from __future__ import annotations

import os
from pathlib import Path

from typer.testing import CliRunner

from riscv_parameter_extractor.cli import app, provider_from_env
from riscv_parameter_extractor.config import load_env_file
from riscv_parameter_extractor.providers import DeepSeekChatProvider

runner = CliRunner()


def test_cli_help() -> None:
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    assert "Extract and validate" in result.output


def test_cli_providers() -> None:
    result = runner.invoke(app, ["providers"])
    assert result.exit_code == 0
    assert "OPENAI_API_KEY" in result.output
    assert "DEEPSEEK_API_KEY" in result.output


def test_provider_from_env_selects_deepseek(monkeypatch) -> None:
    monkeypatch.setenv("DEEPSEEK_API_KEY", "test-key")
    monkeypatch.setenv("RISCV_EXTRACT_PROVIDER", "deepseek")
    monkeypatch.setenv("RISCV_EXTRACT_MODEL", "deepseek-v4-pro")
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)

    provider = provider_from_env()

    assert isinstance(provider, DeepSeekChatProvider)
    assert provider.model_id == "deepseek-v4-pro"


def test_load_env_file(monkeypatch) -> None:
    monkeypatch.delenv("DEEPSEEK_API_KEY", raising=False)
    monkeypatch.delenv("RISCV_EXTRACT_PROVIDER", raising=False)
    monkeypatch.delenv("RISCV_EXTRACT_MODEL", raising=False)

    load_env_file(Path("tests/fixtures/deepseek.env"))

    assert os.environ["DEEPSEEK_API_KEY"] == "test-key"
    assert os.environ["RISCV_EXTRACT_PROVIDER"] == "deepseek"
    assert os.environ["RISCV_EXTRACT_MODEL"] == "deepseek-v4-pro"


def test_cli_validate_final_yaml() -> None:
    result = runner.invoke(app, ["validate"])
    assert result.exit_code == 0
    assert "validation passed" in result.output


def test_cli_evaluate() -> None:
    result = runner.invoke(app, ["evaluate"])
    assert result.exit_code == 0
    assert "wrote results/evaluation_summary.yaml" in result.output
