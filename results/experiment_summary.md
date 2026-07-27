# Experiment Summary

Final submission status: `validated_reviewer_ready`

The final assignment workflow was run with DeepSeek `deepseek-v4-pro` using the
DeepSeek API key loaded from `.env`, then validated and manually reviewed for the
reviewer-facing YAML:

```bash
python -m riscv_parameter_extractor extract
```

The canonical reviewer-facing YAML is `submission/results.yaml`.

The `experiment` command remains deterministic and mock-backed by design so prompt
versions can be compared without spending API credits:

```bash
python -m riscv_parameter_extractor experiment
```
