from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .normalization import normalize_name


@dataclass(frozen=True)
class EvaluationMetrics:
    parameter_precision: float
    parameter_recall: float
    parameter_f1: float
    type_accuracy: float
    parameter_class_accuracy: float
    constraint_precision: float
    constraint_recall: float
    evidence_validity: float
    duplicate_rate: float
    unsupported_claim_count: int
    malformed_output_count: int

    def as_dict(self) -> dict[str, float | int]:
        return {
            "parameter_precision": self.parameter_precision,
            "parameter_recall": self.parameter_recall,
            "parameter_f1": self.parameter_f1,
            "type_accuracy": self.type_accuracy,
            "parameter_class_accuracy": self.parameter_class_accuracy,
            "constraint_precision": self.constraint_precision,
            "constraint_recall": self.constraint_recall,
            "evidence_validity": self.evidence_validity,
            "duplicate_rate": self.duplicate_rate,
            "unsupported_claim_count": self.unsupported_claim_count,
            "malformed_output_count": self.malformed_output_count,
        }


ALIASES = {
    "csr_encoding_space_capacity": {"maximum_csr_count", "csr_encoding_capacity"},
    "csr_address_width": {"csr_address_encoding_width"},
}


def canonical_name(name: str) -> str:
    normalized = normalize_name(name)
    for canonical, aliases in ALIASES.items():
        if normalized == canonical or normalized in aliases:
            return canonical
    return normalized


def _constraint_keys(parameter: dict[str, Any]) -> set[str]:
    return {normalize_name(item["kind"]) for item in parameter.get("constraints", [])}


def evaluate_source(predicted: dict[str, Any], gold: dict[str, Any]) -> EvaluationMetrics:
    predicted_params = predicted.get("parameters", [])
    gold_params = gold.get("parameters", [])
    predicted_by_name = {canonical_name(item["name"]): item for item in predicted_params}
    gold_by_name = {canonical_name(item["name"]): item for item in gold_params}
    duplicate_rate = 0.0
    if predicted_params:
        duplicate_rate = 1.0 - (len(predicted_by_name) / len(predicted_params))
    matched = sorted(set(predicted_by_name) & set(gold_by_name))
    false_positive = set(predicted_by_name) - set(gold_by_name)
    precision = len(matched) / len(predicted_by_name) if predicted_by_name else 1.0
    recall = len(matched) / len(gold_by_name) if gold_by_name else 1.0
    f1 = (2 * precision * recall / (precision + recall)) if precision + recall else 0.0

    type_correct = 0
    class_correct = 0
    pred_constraints = 0
    matched_constraints = 0
    gold_constraints = 0
    valid_evidence = 0
    evidence_count = 0
    for name in matched:
        pred = predicted_by_name[name]
        expected = gold_by_name[name]
        type_correct += int(pred.get("type") == expected.get("type"))
        class_correct += int(pred.get("parameter_class") == expected.get("parameter_class"))
        pred_keys = _constraint_keys(pred)
        gold_keys = _constraint_keys(expected)
        pred_constraints += len(pred_keys)
        gold_constraints += len(gold_keys)
        matched_constraints += len(pred_keys & gold_keys)
        evidence_items = pred.get("evidence", [])
        evidence_count += len(evidence_items)
        valid_evidence += sum(1 for item in evidence_items if item.get("text"))

    type_accuracy = type_correct / len(matched) if matched else 0.0
    class_accuracy = class_correct / len(matched) if matched else 0.0
    constraint_precision = matched_constraints / pred_constraints if pred_constraints else 1.0
    constraint_recall = matched_constraints / gold_constraints if gold_constraints else 1.0
    evidence_validity = valid_evidence / evidence_count if evidence_count else 1.0
    unsupported_claim_count = len(false_positive)
    return EvaluationMetrics(
        parameter_precision=round(precision, 4),
        parameter_recall=round(recall, 4),
        parameter_f1=round(f1, 4),
        type_accuracy=round(type_accuracy, 4),
        parameter_class_accuracy=round(class_accuracy, 4),
        constraint_precision=round(constraint_precision, 4),
        constraint_recall=round(constraint_recall, 4),
        evidence_validity=round(evidence_validity, 4),
        duplicate_rate=round(duplicate_rate, 4),
        unsupported_claim_count=unsupported_claim_count,
        malformed_output_count=0,
    )


def aggregate_metrics(metrics: list[EvaluationMetrics]) -> dict[str, float | int]:
    if not metrics:
        return {}
    totals: dict[str, float] = {}
    for metric in metrics:
        for key, value in metric.as_dict().items():
            totals[key] = totals.get(key, 0.0) + float(value)
    return {key: round(value / len(metrics), 4) for key, value in totals.items()}
