from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from typing import Any, cast

from pydantic import ValidationError

from .models import ExtractionResult

FENCED_JSON_RE = re.compile(r"```(?:json)?\s*(?P<body>.*?)```", re.DOTALL | re.IGNORECASE)
BIT_RANGE_TEXT_RE = re.compile(r"(?:[A-Za-z_][A-Za-z0-9_]*\s*)?\[\d+(?::\d+)?\]")


@dataclass
class ValidationReport:
    ok: bool
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)


def extract_json_object(raw: str) -> str:
    fenced = FENCED_JSON_RE.search(raw)
    candidate = fenced.group("body").strip() if fenced else raw.strip()
    if not candidate:
        raise ValueError("empty model response")
    if candidate.startswith("{"):
        return candidate
    start = candidate.find("{")
    end = candidate.rfind("}")
    if start == -1 or end == -1 or end <= start:
        raise ValueError("no JSON object found in model response")
    return candidate[start : end + 1]


def parse_model_response(raw: str) -> dict[str, Any]:
    try:
        loaded = json.loads(extract_json_object(raw))
    except json.JSONDecodeError as exc:
        raise ValueError(f"malformed JSON: {exc}") from exc
    if not isinstance(loaded, dict):
        raise ValueError("model response must be a JSON object")
    return cast(dict[str, Any], loaded)


def evidence_offsets(snippet: str, evidence: str) -> tuple[int, int]:
    start = snippet.find(evidence)
    if start < 0:
        raise ValueError(f"evidence not found in snippet: {evidence!r}")
    return start, start + len(evidence)


def validate_evidence(result: ExtractionResult, snippet: str) -> ValidationReport:
    report = ValidationReport(ok=True)
    for parameter in result.parameters:
        for evidence in parameter.evidence:
            try:
                start, end = evidence_offsets(snippet, evidence.text)
            except ValueError as exc:
                report.errors.append(f"{parameter.name}: {exc}")
                continue
            if evidence.start is not None and evidence.start != start:
                report.errors.append(f"{parameter.name}: evidence start offset mismatch")
            if evidence.end is not None and evidence.end != end:
                report.errors.append(f"{parameter.name}: evidence end offset mismatch")
        for constraint in parameter.constraints:
            if constraint.evidence is None:
                if constraint.explicit:
                    report.errors.append(
                        f"{parameter.name}: explicit constraint lacks evidence: {constraint.kind}"
                    )
                continue
            try:
                evidence_offsets(snippet, constraint.evidence)
            except ValueError as exc:
                report.errors.append(f"{parameter.name}/{constraint.kind}: {exc}")
        for relationship in parameter.relationships:
            if relationship.evidence is not None:
                try:
                    evidence_offsets(snippet, relationship.evidence)
                except ValueError as exc:
                    report.errors.append(f"{parameter.name}/{relationship.kind}: {exc}")
    report.ok = not report.errors
    return report


def validate_bit_ranges(result: ExtractionResult) -> ValidationReport:
    report = ValidationReport(ok=True)
    for parameter in result.parameters:
        texts = [parameter.name, parameter.description]
        texts.extend(constraint.description for constraint in parameter.constraints)
        for text in texts:
            for bit_range in BIT_RANGE_TEXT_RE.findall(text):
                hi_lo = re.search(r"\[(\d+)(?::(\d+))?\]", bit_range)
                if hi_lo and hi_lo.group(2) and int(hi_lo.group(1)) < int(hi_lo.group(2)):
                    report.errors.append(f"{parameter.name}: invalid bit range {bit_range}")
    report.ok = not report.errors
    return report


def validate_source_metadata(
    result: ExtractionResult,
    expected_source_id: str | None = None,
    expected_source_label: str | None = None,
) -> ValidationReport:
    report = ValidationReport(ok=True)
    if "{{" in result.source.id or "}}" in result.source.id:
        report.errors.append("source.id contains an unresolved template placeholder")
    if "{{" in result.source.label or "}}" in result.source.label:
        report.errors.append("source.label contains an unresolved template placeholder")
    if expected_source_id is not None and result.source.id != expected_source_id:
        report.errors.append(
            f"source.id mismatch: expected {expected_source_id!r}, got {result.source.id!r}"
        )
    if expected_source_label is not None and result.source.label != expected_source_label:
        report.errors.append(
            f"source.label mismatch: expected {expected_source_label!r}, "
            f"got {result.source.label!r}"
        )
    report.ok = not report.errors
    return report


def validate_response(
    raw: str,
    snippet: str,
    expected_source_id: str | None = None,
    expected_source_label: str | None = None,
) -> tuple[ExtractionResult | None, ValidationReport]:
    errors: list[str] = []
    try:
        payload = parse_model_response(raw)
        result = ExtractionResult.model_validate(payload)
    except (ValueError, ValidationError) as exc:
        return None, ValidationReport(ok=False, errors=[str(exc)])

    source_report = validate_source_metadata(result, expected_source_id, expected_source_label)
    evidence_report = validate_evidence(result, snippet)
    bit_report = validate_bit_ranges(result)
    errors.extend(source_report.errors)
    errors.extend(evidence_report.errors)
    errors.extend(bit_report.errors)
    warnings = source_report.warnings + evidence_report.warnings + bit_report.warnings
    return result, ValidationReport(ok=not errors, errors=errors, warnings=warnings)
