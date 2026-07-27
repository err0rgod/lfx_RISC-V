# RISC-V Parameter Extractor

This repository is a complete, reproducible submission for the LFX Mentorship challenge on AI-assisted extraction of architectural parameters from RISC-V specification snippets.

## Approach

The project treats a parameter as a structured architectural property affecting implementation, architecture, encoding, capacity, organization, limits, bit ranges, or behavior. The final prompt is source-only and evidence-grounded. The validator rejects malformed JSON, duplicate names, invalid enum values, unknown fields, and evidence that is not an exact substring of the input snippet.

## Key Decisions

- Cache capacity, cache organization, and cache-block size are separate implementation-specific parameters.
- Cache-block power-of-two/NAPOT and natural-alignment wording is attached to cache-block size only.
- Cache information discoverability is modeled as a separate architectural property and referenced as a constraint.
- CSR `csr[11:8]` is a composite accessibility field; `csr[11:10]` and `csr[9:8]` are linked subfields.
- The output does not add privilege-level value meanings absent from the snippet.

## Repository Structure

- `src/riscv_parameter_extractor/`: package, schemas, validation, providers, evaluation, CLI.
- `inputs/`: exact supplied snippets.
- `prompts/`: V1, V2, V3, and final prompt.
- `gold/`: human-reviewed gold standard and annotation notes.
- `results/`: generated results and experiment summaries.
- `reports/`: prompt, model, evaluation, hallucination, and source notes.
- `submission/`: reviewer-facing artifacts.
- `tests/`: validation, normalization, provider, evaluation, and CLI tests.

## Installation

```bash
python -m pip install -e ".[dev]"
```

## Environment

Copy `.env.example` if needed. Do not commit real keys. The CLI loads simple `KEY=VALUE`
pairs from `.env` automatically and does not print secret values.

For a live DeepSeek run:

```env
DEEPSEEK_API_KEY=your_key_here
RISCV_EXTRACT_PROVIDER=deepseek
RISCV_EXTRACT_MODEL=deepseek-v4-pro
```

Without a configured live provider key, the deterministic mock provider is used.

## CLI

```bash
riscv-extract providers
riscv-extract extract
riscv-extract experiment
riscv-extract validate
riscv-extract evaluate
riscv-extract build-submission
```

`extract` writes live or mock output to `results/final_results.yaml`.
`experiment` is intentionally deterministic and mock-backed by the human-reviewed
gold annotations so prompt files can be exercised without API spend.

Equivalent module form:

```bash
python -m riscv_parameter_extractor validate
```

## Prompt Versions

V1 is a keyword baseline. V2 expands to semantic architectural parameters. V3 adds exact evidence and controlled schemas. The final prompt generalizes V3 and avoids answer leakage.

## Validation and Evaluation

Validation is deterministic and does not require an LLM. Evaluation uses the human-reviewed gold standard and reports precision, recall, F1, type accuracy, class accuracy, constraint metrics, evidence validity, duplicate rate, unsupported claims, and malformed output count.

## Results Summary

Final results are in `submission/results.yaml`. The assignment workflow used
DeepSeek `deepseek-v4-pro` through the OpenAI-compatible Chat Completions API, with
strict schema validation, exact-evidence validation, and reviewer curation.

## Reproducibility

Commands used:

```bash
python -m riscv_parameter_extractor validate
python -m riscv_parameter_extractor experiment
python -m riscv_parameter_extractor evaluate
python -m pytest
python -m ruff check .
python -m ruff format --check .
python -m mypy src
```

If `mypy` is not installed, install the development dependencies first.

## Submission Artifacts

- Main submission: `submission/coding_challenge_submission.md`
- Model metadata: `submission/model_details.yaml`
- Prompt summary: `submission/prompts.md`
- Final extraction YAML: `submission/results.yaml`
