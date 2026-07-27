from __future__ import annotations

import os
import shutil
from pathlib import Path
from typing import Annotated

import typer
from rich.console import Console

from .config import available_providers, first_available_provider, load_env_file
from .evaluation import aggregate_metrics, evaluate_source
from .extraction import run_extraction
from .models import Snippet
from .providers import DeepSeekChatProvider, MockProvider, OpenAIResponsesProvider
from .utils import read_text, read_yaml, write_yaml
from .validation import validate_response

app = typer.Typer(help="Extract and validate RISC-V architectural parameters.")
console = Console()

DEFAULT_PROMPT_PATH = Path("prompts/final_prompt.txt")
DEFAULT_RESULTS_PATH = Path("results/final_results.yaml")
DEFAULT_SUBMISSION_RESULTS_PATH = Path("submission/results.yaml")
DEFAULT_SNIPPETS_PATH = Path("inputs/snippets.yaml")
DEFAULT_GOLD_PATH = Path("gold/gold_standard.yaml")


def load_snippets(path: Path = Path("inputs/snippets.yaml")) -> list[Snippet]:
    data = read_yaml(path)
    return [Snippet.model_validate(item) for item in data["snippets"]]


def provider_from_env() -> MockProvider | OpenAIResponsesProvider | DeepSeekChatProvider:
    load_env_file()
    provider = os.getenv("RISCV_EXTRACT_PROVIDER", "mock").lower()
    if provider == "deepseek" and os.getenv("DEEPSEEK_API_KEY"):
        return DeepSeekChatProvider(
            api_key=os.environ["DEEPSEEK_API_KEY"],
            model_id=os.getenv("RISCV_EXTRACT_MODEL", "deepseek-v4-pro"),
        )
    if provider == "openai" and os.getenv("OPENAI_API_KEY"):
        return OpenAIResponsesProvider(
            api_key=os.environ["OPENAI_API_KEY"],
            model_id=os.getenv("RISCV_EXTRACT_MODEL", "gpt-4.1-mini"),
        )
    return MockProvider()


@app.command()
def providers() -> None:
    """Show which provider environment variables are present without printing values."""
    load_env_file()
    for provider in available_providers():
        status = "present" if provider.present else "missing"
        console.print(f"{provider.provider}: {provider.env_var} {status}")
    console.print(f"selected_live_provider: {first_available_provider() or 'none'}")


@app.command()
def extract(
    prompt_path: Annotated[Path, typer.Option()] = DEFAULT_PROMPT_PATH,
    output_path: Annotated[Path, typer.Option()] = DEFAULT_RESULTS_PATH,
) -> None:
    """Run extraction for all snippets with the configured provider."""
    prompt_text = read_text(prompt_path)
    provider = provider_from_env()
    outputs = []
    for snippet in load_snippets():
        result, record = run_extraction(provider, prompt_path.stem, prompt_text, snippet)
        console.print(
            f"{snippet.id}: {record.validation_status} ({record.provider}/{record.model_id})"
        )
        if result is not None:
            outputs.append(result.model_dump(mode="json"))
    write_yaml(output_path, {"results": outputs})
    console.print(f"wrote {output_path}")


@app.command()
def experiment() -> None:
    """Run deterministic mock experiments for all prompt versions."""
    records = []
    provider = MockProvider()
    for prompt_path in sorted(Path("prompts").glob("*.txt")):
        prompt_text = read_text(prompt_path)
        for snippet in load_snippets():
            _result, record = run_extraction(provider, prompt_path.stem, prompt_text, snippet)
            records.append(record.model_dump(mode="json"))
    write_yaml(Path("results/experiment_summary.yaml"), {"status": "mock_only", "runs": records})
    console.print("wrote results/experiment_summary.yaml")


@app.command()
def validate(
    results_path: Annotated[Path, typer.Option()] = DEFAULT_SUBMISSION_RESULTS_PATH,
    snippets_path: Annotated[Path, typer.Option()] = DEFAULT_SNIPPETS_PATH,
) -> None:
    """Validate final YAML against schemas and exact evidence rules."""
    results = read_yaml(results_path)
    snippets = {item.id: item for item in load_snippets(snippets_path)}
    failures = []
    for source in results["results"]:
        source_id = source["source"]["id"]
        snippet = snippets.get(source_id)
        if snippet is None:
            failures.append(f"unknown source id: {source_id}")
            continue
        raw = __import__("json").dumps(source)
        _result, report = validate_response(
            raw,
            snippet.text,
            expected_source_id=snippet.id,
            expected_source_label=snippet.label,
        )
        if not report.ok:
            failures.extend(report.errors)
    if failures:
        for failure in failures:
            console.print(f"[red]FAIL[/red] {failure}")
        raise typer.Exit(1)
    console.print("validation passed")


@app.command()
def evaluate(
    results_path: Annotated[Path, typer.Option()] = DEFAULT_SUBMISSION_RESULTS_PATH,
    gold_path: Annotated[Path, typer.Option()] = DEFAULT_GOLD_PATH,
) -> None:
    """Evaluate final results against the deterministic human-reviewed gold file."""
    results = read_yaml(results_path)["results"]
    gold = read_yaml(gold_path)["sources"]
    metrics = [
        evaluate_source(predicted, expected).as_dict()
        for predicted, expected in zip(results, gold, strict=True)
    ]
    aggregate = aggregate_metrics(
        [evaluate_source(p, g) for p, g in zip(results, gold, strict=True)]
    )
    write_yaml(
        Path("results/evaluation_summary.yaml"),
        {"per_source": metrics, "aggregate": aggregate},
    )
    console.print("wrote results/evaluation_summary.yaml")
    console.print(aggregate)


@app.command("build-submission")
def build_submission() -> None:
    """Refresh reviewer-facing submission artifacts from canonical files."""
    shutil.copyfile("results/final_results.yaml", "submission/results.yaml")
    shutil.copyfile("reports/model_details.yaml", "submission/model_details.yaml")
    console.print("submission artifacts refreshed")
