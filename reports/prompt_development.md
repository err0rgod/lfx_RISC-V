# Prompt Development

## Initial Hypothesis

The challenge text highlights modal and variability words such as "implementation-specific". A naive baseline can find some implementation-specific parameters, but it will miss fixed architectural constants and bit encodings.

## V1 Keyword Baseline

V1 searches for trigger words including may, might, should, optional, implementation-defined, and implementation-specific. It is credible but weak: the CSR snippet has no highlighted trigger words, so a keyword-only prompt is likely to miss the 12-bit CSR address space, the CSR bit ranges, and the read/write value encodings.

## V2 Semantic Extraction

V2 broadens the definition of a parameter to cover implementation choices, constants, limits, bitfields, and encodings. This improves recall for the CSR snippet, but without strict evidence and deduplication rules it can over-split sentence fragments or attach unsupported constraints to the wrong parameter.

## V3 Evidence-Grounded Extraction

V3 adds exact evidence spans, controlled enums, explicit/inferred constraint handling, deduplication, relationship handling, and source-only rules. The main remaining risk is annotation judgment around borderline architectural properties such as cache information discoverability.

## Final Prompt Rationale

The final prompt keeps V3's evidence discipline and adds clearer inclusion/exclusion criteria. It explicitly tells the model not to add privilege-level value meanings unless stated and to use relationships for composite fields and subfields.

## Observed Failure Modes

- Keyword-only extraction misses architectural constants with no modal words.
- Broad semantic extraction may extract ordinary nouns such as "software" or "Table 1".
- Models may invent units for cache capacity or block size.
- Models may add RISC-V privilege value meanings not present in the snippet.
- Models may duplicate `csr[11:8]` and its subfields as unrelated parameters.

## Hallucination-Reduction Techniques

- Exact evidence is required for every parameter and explicit constraint.
- A validator rejects evidence not found in the input snippet.
- Controlled enums reject unsupported type, class, and confidence values.
- Relationship fields represent composite/subfield structure without treating everything as an independent implementation choice.
- The extraction prompt forbids external RISC-V knowledge.
