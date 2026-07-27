from __future__ import annotations

from pathlib import Path
from typing import Any

import pytest
import yaml


@pytest.fixture
def snippets() -> list[dict[str, Any]]:
    return yaml.safe_load(Path("inputs/snippets.yaml").read_text(encoding="utf-8"))["snippets"]


@pytest.fixture
def final_results() -> dict[str, Any]:
    return yaml.safe_load(Path("submission/results.yaml").read_text(encoding="utf-8"))
