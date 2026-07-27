from __future__ import annotations

import json

import pytest

from riscv_parameter_extractor.models import ExtractionResult
from riscv_parameter_extractor.validation import (
    evidence_offsets,
    extract_json_object,
    parse_model_response,
    validate_evidence,
    validate_response,
)


def payload_with_evidence(evidence: str) -> dict[str, object]:
    return {
        "source": {"id": "s1", "label": "S1"},
        "parameters": [
            {
                "name": "cache_capacity",
                "description": "Cache capacity.",
                "type": "integer",
                "parameter_class": "implementation_specific",
                "constraints": [
                    {
                        "kind": "implementation_specific",
                        "description": "Implementation-specific.",
                        "explicit": True,
                        "evidence": evidence,
                    }
                ],
                "evidence": [{"text": evidence, "start": None, "end": None}],
                "confidence": "high",
                "relationships": [],
                "notes": None,
            }
        ],
    }


def test_exact_evidence_validation(snippets: list[dict[str, str]]) -> None:
    snippet = snippets[0]["text"]
    evidence = (
        "The capacity and organization of a cache and the size of a cache block "
        "are both implementation-specific"
    )
    result = ExtractionResult.model_validate(payload_with_evidence(evidence))
    report = validate_evidence(result, snippet)
    assert report.ok


def test_evidence_mismatch_rejected(snippets: list[dict[str, str]]) -> None:
    result = ExtractionResult.model_validate(payload_with_evidence("not in snippet"))
    report = validate_evidence(result, snippets[0]["text"])
    assert not report.ok
    assert "evidence not found" in report.errors[0]


def test_substring_offsets(snippets: list[dict[str, str]]) -> None:
    evidence = "up to 4,096 CSRs"
    start, end = evidence_offsets(snippets[1]["text"], evidence)
    assert snippets[1]["text"][start:end] == evidence


def test_json_extraction_from_fenced_model_output() -> None:
    raw = '```json\n{"source":{"id":"s","label":"S"},"parameters":[]}\n```'
    assert parse_model_response(raw)["parameters"] == []


def test_malformed_json() -> None:
    with pytest.raises(ValueError, match="malformed JSON"):
        parse_model_response('{"source":')


def test_no_json_object_found() -> None:
    with pytest.raises(ValueError, match="no JSON object"):
        extract_json_object("plain text")


def test_validate_response_accepts_empty_parameters() -> None:
    raw = json.dumps({"source": {"id": "s", "label": "S"}, "parameters": []})
    result, report = validate_response(raw, "irrelevant")
    assert report.ok
    assert result is not None


def test_validate_response_rejects_source_placeholders() -> None:
    raw = json.dumps(
        {"source": {"id": "{{source_id}}", "label": "{{source_label}}"}, "parameters": []}
    )
    _result, report = validate_response(
        raw,
        "irrelevant",
        expected_source_id="s1",
        expected_source_label="S1",
    )
    assert not report.ok
    assert "source.id contains an unresolved template placeholder" in report.errors
