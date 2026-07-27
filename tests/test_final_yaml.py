from __future__ import annotations

import yaml

from riscv_parameter_extractor.cli import load_snippets
from riscv_parameter_extractor.validation import validate_response


def test_final_yaml_generation_and_validation(final_results: dict[str, object]) -> None:
    serialized = yaml.safe_dump(final_results, sort_keys=False)
    loaded = yaml.safe_load(serialized)
    snippets = {snippet.id: snippet for snippet in load_snippets()}
    for source in loaded["results"]:
        snippet = snippets[source["source"]["id"]]
        raw = __import__("json").dumps(source)
        _result, report = validate_response(raw, snippet.text)
        assert report.ok, report.errors
