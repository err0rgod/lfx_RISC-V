# Evaluation

The evaluator compares normalized parameter names against a human-reviewed gold standard and uses deterministic alias mappings where appropriate. It also checks type accuracy, parameter-class accuracy, constraint precision/recall, evidence validity, duplicate rate, unsupported-claim count, and malformed-output count.

Because the dataset contains only two snippets, the metrics are useful as engineering checks rather than statistically meaningful benchmark claims.

## Gold-Standard Approach

The gold standard was manually annotated from only the supplied snippets. Ambiguous decisions are documented in `gold/annotation_notes.md`.

## Prompt-Level Discussion

- V1 is expected to have low recall on the CSR snippet because it focuses on modal keywords.
- V2 improves recall by including constants, bitfields, limits, and encodings.
- V3 and the final prompt add exact evidence, controlled schema values, and relationship handling.

## Current Run Status

The final assignment workflow was run live with DeepSeek `deepseek-v4-pro` using
`python -m riscv_parameter_extractor extract`, followed by validation and manual
review for the submitted YAML. The repository also keeps the gold-backed
deterministic mock provider for repeatable local tests and prompt experiments.

Run:

```bash
python -m riscv_parameter_extractor validate --results-path submission/results.yaml
python -m riscv_parameter_extractor evaluate --results-path submission/results.yaml
```

The generated evaluation summary is written to `results/evaluation_summary.yaml`.
