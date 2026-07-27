# RISC-V Parameter Extractor

This repository is my submission for the LFX Mentorship coding challenge:
AI-assisted extraction of architectural parameters from RISC-V specification
snippets.

The goal is not only to provide the final YAML answer, but also to show how the
prompt was developed, which LLM was used, how hallucinations were controlled, and
how the output can be validated.

## What To Read First

If you are reviewing the submission, start here:

- `submission/coding_challenge_submission.md`: main writeup for the challenge.
- `submission/results.yaml`: final extracted parameters in YAML format.
- `submission/model_details.yaml`: LLM and run metadata.
- `submission/prompts.md`: short summary of the prompt iterations.
- `prompts/final_prompt.txt`: actual final prompt used for extraction.

## Plain-English Approach

The assignment asks for architectural parameters from two RISC-V ISA Manual
snippets. I treated a parameter as any structured property that affects
implementation, encoding, capacity, organization, limits, bit ranges, legal values,
or required behavior.

The prompt tells the model to use only the supplied snippet. It must return
structured JSON, and every parameter or explicit constraint must include exact
evidence copied from the snippet. The code then validates that output before it is
accepted into the final YAML.

This is important because the challenge keywords such as `may`, `optional`, and
`implementation-specific` are useful clues, but they are not enough. The CSR snippet,
for example, contains fixed architectural constants and bitfield encodings without
those trigger words.

## Important Modeling Decisions

- Cache capacity, cache organization, and cache-block size are separate
  implementation-specific parameters.
- Cache-block natural alignment and power-of-two/NAPOT wording are attached to
  cache-block size, not to cache capacity.
- Cache information discoverability is represented because the snippet says the
  execution environment provides software a way to discover cache information.
- CSR `csr[11:8]` is modeled as a composite accessibility field.
- CSR `csr[11:10]` and `csr[9:8]` are modeled as subfields of that composite field.
- The output does not invent privilege-level value meanings that are absent from the
  supplied snippet.

## File Guide

### Reviewer-Facing Files

- `submission/coding_challenge_submission.md`: complete challenge response with
  LLM details, prompt development, hallucination controls, results, and commands.
- `submission/results.yaml`: final answer in the requested YAML format.
- `submission/model_details.yaml`: machine-readable model information such as
  provider, model id, context length, output limit, temperature, and endpoint.
- `submission/prompts.md`: concise explanation of V1, V2, V3, and final prompt.
- `submission/README.md`: small index of the submission files.

### Inputs, Prompts, And Expected Output

- `inputs/snippets.yaml`: the two supplied RISC-V snippets.
- `prompts/v1_keyword_baseline.txt`: first prompt based mainly on challenge trigger
  words.
- `prompts/v2_semantic_extraction.txt`: broader prompt that also extracts constants,
  limits, bitfields, and encodings.
- `prompts/v3_evidence_grounded.txt`: adds exact evidence, controlled values,
  deduplication, and source-only rules.
- `prompts/final_prompt.txt`: polished final prompt for the submitted workflow.
- `gold/gold_standard.yaml`: human-reviewed expected extraction used for evaluation
  and deterministic mock tests.
- `gold/annotation_notes.md`: explains the reasoning behind ambiguous modeling
  decisions.

### Source Code

- `src/riscv_parameter_extractor/models.py`: Pydantic schema for sources,
  parameters, constraints, evidence, confidence, and relationships.
- `src/riscv_parameter_extractor/validation.py`: validates JSON, exact evidence
  substrings, duplicate names, source metadata, and bit ranges.
- `src/riscv_parameter_extractor/providers.py`: LLM provider integrations for
  DeepSeek, OpenAI-compatible calls, and the deterministic mock provider.
- `src/riscv_parameter_extractor/extraction.py`: renders prompts, calls the selected
  provider, validates responses, and writes normalized output.
- `src/riscv_parameter_extractor/evaluation.py`: compares final results with the
  human-reviewed gold file and computes metrics.
- `src/riscv_parameter_extractor/cli.py`: command-line interface for extraction,
  validation, evaluation, provider checks, and submission building.
- `src/riscv_parameter_extractor/config.py`: loads environment variables and
  determines available providers.
- `src/riscv_parameter_extractor/normalization.py`: normalizes names and bit ranges.
- `src/riscv_parameter_extractor/utils.py`: small file, YAML, JSON, and hashing
  helpers.

### Reports And Results

- `reports/prompt_development.md`: how the prompt was refined.
- `reports/hallucination_analysis.md`: hallucination risks and controls.
- `reports/evaluation.md`: evaluation method and limitations.
- `reports/model_details.md` and `reports/model_details.yaml`: model/run details.
- `reports/source_notes.md`: notes on using only the supplied snippets.
- `results/final_results.yaml`: canonical final result used to build the submission
  result.
- `results/evaluation_summary.yaml`: metrics from evaluating the final result.
- `results/experiment_summary.md` and `results/experiment_summary.yaml`: deterministic
  mock-backed experiment records.

### Tests And Project Files

- `tests/`: unit tests for schema validation, evidence validation, final YAML,
  evaluation, providers, CLI behavior, and normalization.
- `scripts/`: helper scripts for running experiments, validation, and building
  submission artifacts.
- `pyproject.toml`: package metadata, dependencies, and test/lint/type-check config.
- `Makefile`: shortcut commands.
- `.env.example`: template for optional API keys. It contains no real secrets.
- `.gitignore`: excludes secrets, caches, generated raw outputs, and build artifacts.
- `LICENSE`: MIT license.

## LLM Used

The assignment workflow used DeepSeek `deepseek-v4-pro` through DeepSeek's
OpenAI-compatible Chat Completions API.

Key settings:

- Provider: DeepSeek
- Model: `deepseek-v4-pro`
- Context length: 1M tokens
- Maximum output: 384K tokens
- Temperature: 0
- Structured output: JSON object response format
- Thinking mode: disabled

Full details are in `submission/model_details.yaml`.

## Validation

Validation is deterministic and does not require an LLM. It checks:

- malformed JSON
- unknown schema fields
- invalid enum values
- duplicate parameter names
- evidence strings that are not exact substrings of the input snippet
- source id/label mismatch
- malformed bit ranges

Run:

```bash
python -m riscv_parameter_extractor validate --results-path submission/results.yaml
```

## Evaluation

Evaluation compares the final YAML against the human-reviewed gold standard. Because
there are only two snippets, these metrics are engineering checks, not a broad
benchmark.

Run:

```bash
python -m riscv_parameter_extractor evaluate --results-path submission/results.yaml
```

## Installation

```bash
python -m pip install -e ".[dev]"
```

## Optional Environment Setup

The project works without an API key by using the deterministic mock provider.

For a live DeepSeek run, the local `.env` file uses these keys:

```env
DEEPSEEK_API_KEY=
RISCV_EXTRACT_PROVIDER=deepseek
RISCV_EXTRACT_MODEL=deepseek-v4-pro
```

The local `.env` file is excluded by `.gitignore`.

## Commands

```bash
python -m riscv_parameter_extractor providers
python -m riscv_parameter_extractor extract
python -m riscv_parameter_extractor experiment
python -m riscv_parameter_extractor validate --results-path submission/results.yaml
python -m riscv_parameter_extractor evaluate --results-path submission/results.yaml
python -m pytest -p no:cacheprovider
python -m ruff check --no-cache .
python -m mypy src
```

`experiment` is intentionally deterministic and mock-backed by the human-reviewed
gold annotations, so it can exercise the pipeline without API spend. `extract` uses
DeepSeek only when the DeepSeek environment variables are configured.
