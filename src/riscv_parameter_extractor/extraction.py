from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path

from .models import ExperimentRecord, ExtractionResult, Snippet
from .providers import LLMProvider
from .utils import sha256_text, write_json, write_text, write_yaml
from .validation import validate_response


def render_prompt(prompt_text: str, snippet: Snippet) -> str:
    return (
        prompt_text.replace("{{source_id}}", snippet.id)
        .replace("{{source_label}}", snippet.label)
        .replace("{{snippet}}", snippet.text)
    )


def run_extraction(
    provider: LLMProvider,
    prompt_version: str,
    prompt_text: str,
    snippet: Snippet,
    raw_dir: Path = Path("results/raw"),
    normalized_dir: Path = Path("results/normalized"),
) -> tuple[ExtractionResult | None, ExperimentRecord]:
    rendered_prompt = render_prompt(prompt_text, snippet)
    response = provider.complete(rendered_prompt, snippet.text)
    raw_hash = sha256_text(response.text)
    prefix = f"{prompt_version}_{snippet.id}_{raw_hash[:12]}"
    raw_path = raw_dir / f"{prefix}.json"
    write_text(raw_path, response.text)

    result, report = validate_response(
        response.text,
        snippet.text,
        expected_source_id=snippet.id,
        expected_source_label=snippet.label,
    )
    normalized_path: Path | None = None
    if result is not None and report.ok:
        normalized_path = normalized_dir / f"{prefix}.yaml"
        write_yaml(normalized_path, result.model_dump(mode="json"))
    elif result is not None:
        error_path = normalized_dir / f"{prefix}.validation_errors.json"
        write_json(error_path, {"errors": report.errors, "warnings": report.warnings})

    record = ExperimentRecord(
        timestamp=datetime.now(UTC).isoformat(),
        prompt_version=prompt_version,
        prompt_hash=sha256_text(prompt_text),
        snippet_id=snippet.id,
        snippet_hash=sha256_text(snippet.text),
        provider=response.provider,
        model_id=response.model_id,
        inference_settings={"temperature": 0, "structured_output": True},
        raw_response_path=str(raw_path.as_posix()),
        raw_response_hash=raw_hash,
        validation_status="valid" if report.ok else "invalid",
        normalized_output_path=str(normalized_path.as_posix()) if normalized_path else None,
        latency_seconds=round(response.latency_seconds, 6),
        token_usage=response.token_usage,
        error_message="; ".join(report.errors) if report.errors else None,
    )
    return result if report.ok else None, record
