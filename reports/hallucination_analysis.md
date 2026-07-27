# Hallucination Analysis

The extraction system is designed around source-grounded validation.

External knowledge contamination is prevented by prompt rules and by final review. The CSR output does not add privilege-level value meanings because those meanings are absent from the snippet.

Invented units and ranges are prevented by omission. Cache capacity and cache-block size are marked as implementation-specific, but no byte units or numeric sizes are added.

Unsupported enum values are controlled through Pydantic `StrEnum` fields for parameter type, parameter class, and confidence.

Constraints attached to the wrong parameter are addressed by manual gold annotations and relationship modeling. The power-of-two/NAPOT range is attached to `cache_block_size`, not to cache capacity.

Trigger-word false positives are reduced by requiring a parameter-like architectural role, not merely a modal word. Missing parameters without trigger words are reduced by the semantic definition that includes constants, bitfields, limits, and encodings.

Invalid evidence is rejected programmatically. Every evidence string must be an exact substring of the supplied snippet.

Overconfident outputs are limited by the `confidence` field and by notes for ambiguous modeling choices such as cache discoverability.
