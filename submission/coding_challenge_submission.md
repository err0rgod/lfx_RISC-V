# Coding Challenge: AI-Assisted Extraction of Architectural Parameters

Candidate: Nirbhay Katiyar

## Objective

This submission extracts architectural parameters from two RISC-V Privileged ISA
Manual snippets and formats the result as evidence-grounded YAML. The extraction
pipeline uses a prompt-driven LLM call, then validates the response against a strict
schema and exact evidence rules.

## LLM Details

The assignment workflow used DeepSeek's OpenAI-compatible Chat Completions API. Raw
model responses are schema-validated and evidence-checked before normalization. The
submitted YAML is the reviewer-ready, manually reviewed extraction produced under
that prompt/schema workflow.

| Field | Value |
| --- | --- |
| Provider | DeepSeek |
| Model | `deepseek-v4-pro` |
| Public name | DeepSeek-V4-Pro |
| Context length | 1M tokens |
| Maximum output | 384K tokens |
| Temperature | 0 |
| Max output tokens used | 2000 |
| Thinking mode | Disabled |
| Structured output | JSON object response format |
| API call method | Raw HTTP POST with `httpx` |
| Endpoint | `https://api.deepseek.com/chat/completions` |
| Run date | 2026-07-26 |

Supporting metadata is provided in `submission/model_details.yaml`.

## Prompt Development

The prompt was developed in four stages:

- `v1_keyword_baseline.txt`: started with the challenge's suggested trigger words
  such as "may", "should", "optional", "implementation-defined", and
  "implementation-specific".
- `v2_semantic_extraction.txt`: expanded beyond keyword matching so constants,
  limits, encodings, and bitfields could be extracted from the CSR snippet even when
  those trigger words are absent.
- `v3_evidence_grounded.txt`: added exact evidence requirements, controlled enum
  values, explicit/inferred constraint handling, deduplication, and relationships.
- `final_prompt.txt`: generalized the V3 approach for unseen RISC-V snippets and
  added stronger anti-hallucination rules.

The final prompt requires the model to return only JSON matching the target schema.
It explicitly forbids external RISC-V knowledge, invented units, invented ranges,
unsupported value meanings, and duplicate names.

## Hallucination Controls

The model output is not accepted directly. The validator checks:

- malformed JSON
- unknown fields
- invalid enum values
- duplicate parameter names
- evidence strings that are not exact substrings of the source snippet
- unresolved source placeholders
- mismatched source id or label
- malformed bit ranges

This is important for the CSR snippet because the model must not invent meanings for
privilege-level encodings that are not present in the supplied text.

## Results

The final reviewer-ready YAML is in `submission/results.yaml`. It contains:

- cache capacity, organization, block size, block-size constraints, and cache
  discoverability from Privileged Spec 19.3.1
- CSR address width, CSR encoding-space capacity, the upper accessibility field,
  and CSR subfield encodings from Privileged Spec 2.1

Each parameter includes a normalized name, description, type, parameter class,
constraints, exact evidence, confidence, and relationships where useful.

## Validation

The submitted YAML validates successfully:

```bash
python -m riscv_parameter_extractor validate --results-path submission/results.yaml
```

Evaluation against the human-reviewed gold file is included as an engineering check,
not as an independent benchmark:

```text
parameter_precision: 1.0
parameter_recall: 1.0
parameter_f1: 1.0
type_accuracy: 1.0
parameter_class_accuracy: 1.0
constraint_precision: 1.0
constraint_recall: 1.0
evidence_validity: 1.0
duplicate_rate: 0.0
unsupported_claim_count: 0.0
malformed_output_count: 0.0
```

## Reproduction Commands

```bash
python -m pip install -e ".[dev]"
python -m riscv_parameter_extractor providers
python -m riscv_parameter_extractor extract
python -m riscv_parameter_extractor validate --results-path submission/results.yaml
python -m riscv_parameter_extractor evaluate --results-path submission/results.yaml
python -m pytest
python -m ruff check .
python -m mypy src
```

Note: `python -m riscv_parameter_extractor experiment` is deterministic and
mock-backed by the human-reviewed gold annotations, so it is useful for validating
the pipeline shape without API spend. The live DeepSeek path is exercised through
`python -m riscv_parameter_extractor extract` when `DEEPSEEK_API_KEY` and
`RISCV_EXTRACT_PROVIDER=deepseek` are configured.

## Relevant Paths

- Inputs: `inputs/snippets.yaml`
- Final prompt: `prompts/final_prompt.txt`
- Prompt history: `prompts/`
- Model details: `submission/model_details.yaml`
- Final YAML: `submission/results.yaml`
- Validation and extraction code: `src/riscv_parameter_extractor/`
