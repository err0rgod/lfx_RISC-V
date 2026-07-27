# Prompts

## V1 Keyword Baseline

See `prompts/v1_keyword_baseline.txt`.

Rationale: establish a simple baseline driven by modal and variability keywords. Expected weakness: misses CSR constants and encodings without trigger words.

## V2 Semantic Extraction

See `prompts/v2_semantic_extraction.txt`.

Rationale: broaden extraction to constants, limits, bitfields, encodings, and implementation choices. Remaining weakness: weaker evidence discipline and possible over-splitting.

## V3 Evidence-Grounded

See `prompts/v3_evidence_grounded.txt`.

Rationale: require exact evidence, source-only extraction, controlled enums, deduplication, relationships, and abstention behavior.

## Final Prompt

See `prompts/final_prompt.txt`.

Rationale: polish V3 into a general reusable prompt for unseen RISC-V specification snippets. It does not include answers specific to the two challenge snippets.
