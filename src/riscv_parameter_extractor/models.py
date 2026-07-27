from __future__ import annotations

from enum import StrEnum
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


class ParameterType(StrEnum):
    INTEGER = "integer"
    BOOLEAN = "boolean"
    STRING = "string"
    ENUM = "enum"
    BITFIELD = "bitfield"
    RANGE = "range"
    STRUCTURED = "structured"
    UNKNOWN = "unknown"


class ParameterClass(StrEnum):
    IMPLEMENTATION_SPECIFIC = "implementation_specific"
    IMPLEMENTATION_DEFINED = "implementation_defined"
    ARCHITECTURAL_CONSTANT = "architectural_constant"
    BITFIELD = "bitfield"
    ENCODING = "encoding"
    ENUMERATION = "enumeration"
    LIMIT = "limit"
    BOOLEAN_FEATURE = "boolean_feature"
    OPTIONAL_FEATURE = "optional_feature"
    RANGE = "range"
    OTHER = "other"


class Confidence(StrEnum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class RelationshipKind(StrEnum):
    CONTAINS = "contains"
    SUBFIELD_OF = "subfield_of"
    DERIVED_FROM = "derived_from"
    RELATED_TO = "related_to"


class EvidenceSpan(BaseModel):
    model_config = ConfigDict(extra="forbid")

    text: str = Field(min_length=1)
    start: int | None = Field(default=None, ge=0)
    end: int | None = Field(default=None, ge=0)

    @model_validator(mode="after")
    def validate_offsets(self) -> EvidenceSpan:
        if self.start is not None and self.end is not None and self.end < self.start:
            raise ValueError("evidence end must be greater than or equal to start")
        return self


class Constraint(BaseModel):
    model_config = ConfigDict(extra="forbid")

    kind: str = Field(min_length=1)
    description: str = Field(min_length=1)
    explicit: bool = True
    evidence: str | None = None
    inference_explanation: str | None = None

    @model_validator(mode="after")
    def inferred_constraints_explain_themselves(self) -> Constraint:
        if not self.explicit and not self.inference_explanation:
            raise ValueError("inferred constraints require inference_explanation")
        return self


class Relationship(BaseModel):
    model_config = ConfigDict(extra="forbid")

    kind: RelationshipKind
    target: str = Field(min_length=1)
    description: str = Field(min_length=1)
    evidence: str | None = None


class SourceRef(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: str = Field(min_length=1)
    label: str = Field(min_length=1)


class Parameter(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str = Field(min_length=1)
    display_name: str | None = None
    description: str = Field(min_length=1)
    type: ParameterType
    parameter_class: ParameterClass
    constraints: list[Constraint] = Field(default_factory=list)
    evidence: list[EvidenceSpan] = Field(default_factory=list)
    confidence: Confidence = Confidence.MEDIUM
    relationships: list[Relationship] = Field(default_factory=list)
    notes: str | None = None

    @field_validator("name")
    @classmethod
    def name_must_not_be_blank(cls, value: str) -> str:
        stripped = value.strip()
        if not stripped:
            raise ValueError("parameter name cannot be blank")
        return stripped


class ExtractionResult(BaseModel):
    model_config = ConfigDict(extra="forbid")

    source: SourceRef
    parameters: list[Parameter] = Field(default_factory=list)

    @model_validator(mode="after")
    def reject_duplicate_names(self) -> ExtractionResult:
        seen: set[str] = set()
        duplicates: set[str] = set()
        for parameter in self.parameters:
            key = parameter.name.strip().lower()
            if key in seen:
                duplicates.add(parameter.name)
            seen.add(key)
        if duplicates:
            raise ValueError(f"duplicate parameter names: {sorted(duplicates)}")
        return self


class Snippet(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: str
    label: str
    text: str


class ExperimentRecord(BaseModel):
    model_config = ConfigDict(extra="forbid")

    timestamp: str
    prompt_version: str
    prompt_hash: str
    snippet_id: str
    snippet_hash: str
    provider: str
    model_id: str
    inference_settings: dict[str, Any]
    raw_response_path: str
    raw_response_hash: str
    validation_status: str
    normalized_output_path: str | None = None
    latency_seconds: float
    token_usage: dict[str, Any] | None = None
    error_message: str | None = None
