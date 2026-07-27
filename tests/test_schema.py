from __future__ import annotations

import pytest
from pydantic import ValidationError

from riscv_parameter_extractor.models import ExtractionResult


def minimal_payload() -> dict[str, object]:
    return {
        "source": {"id": "s1", "label": "S1"},
        "parameters": [
            {
                "name": "csr_address_width",
                "description": "CSR address width.",
                "type": "integer",
                "parameter_class": "architectural_constant",
                "constraints": [],
                "evidence": [{"text": "12-bit encoding space", "start": None, "end": None}],
                "confidence": "high",
                "relationships": [],
                "notes": None,
            }
        ],
    }


def test_valid_schema_parsing() -> None:
    result = ExtractionResult.model_validate(minimal_payload())
    assert result.parameters[0].name == "csr_address_width"


def test_invalid_type_rejected() -> None:
    payload = minimal_payload()
    payload["parameters"][0]["type"] = "number"  # type: ignore[index]
    with pytest.raises(ValidationError):
        ExtractionResult.model_validate(payload)


def test_unknown_enum_rejected() -> None:
    payload = minimal_payload()
    payload["parameters"][0]["confidence"] = "certain"  # type: ignore[index]
    with pytest.raises(ValidationError):
        ExtractionResult.model_validate(payload)


def test_unknown_relationship_kind_rejected() -> None:
    payload = minimal_payload()
    payload["parameters"][0]["relationships"] = [  # type: ignore[index]
        {
            "kind": "describes_discovery_for",
            "target": "cache_capacity",
            "description": "Discovery covers cache capacity.",
            "evidence": "cache",
        }
    ]
    with pytest.raises(ValidationError):
        ExtractionResult.model_validate(payload)


def test_unknown_field_rejected() -> None:
    payload = minimal_payload()
    payload["unexpected"] = True
    with pytest.raises(ValidationError):
        ExtractionResult.model_validate(payload)


def test_duplicate_parameter_detection() -> None:
    payload = minimal_payload()
    payload["parameters"].append(payload["parameters"][0].copy())  # type: ignore[union-attr]
    with pytest.raises(ValidationError, match="duplicate"):
        ExtractionResult.model_validate(payload)


def test_empty_parameter_list_valid() -> None:
    result = ExtractionResult.model_validate(
        {"source": {"id": "s1", "label": "S1"}, "parameters": []}
    )
    assert result.parameters == []
