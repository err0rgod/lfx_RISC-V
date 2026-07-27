from __future__ import annotations

from riscv_parameter_extractor.evaluation import canonical_name, evaluate_source


def test_alias_matching() -> None:
    assert canonical_name("maximum_csr_count") == "csr_encoding_space_capacity"


def test_evaluation_metrics(final_results: dict[str, object]) -> None:
    predicted = final_results["results"][0]  # type: ignore[index]
    metrics = evaluate_source(predicted, predicted)  # type: ignore[arg-type]
    assert metrics.parameter_precision == 1.0
    assert metrics.parameter_recall == 1.0
    assert metrics.parameter_f1 == 1.0


def test_unsupported_constraints_counted(final_results: dict[str, object]) -> None:
    predicted = {
        "source": {"id": "s", "label": "S"},
        "parameters": [
            {
                "name": "invented_parameter",
                "type": "integer",
                "parameter_class": "limit",
                "constraints": [],
            }
        ],
    }
    metrics = evaluate_source(predicted, final_results["results"][0])  # type: ignore[index]
    assert metrics.unsupported_claim_count == 1
