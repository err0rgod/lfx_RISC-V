# Annotation Notes

The gold standard is based only on the two supplied snippets.

Cache snippet decisions:

- `cache_capacity`, `cache_organization`, and `cache_block_size` are separate because capacity, organization, and block size can vary independently.
- The naturally aligned power-of-two/NAPOT range is attached to `cache_block_size`; it is not attached to cache capacity.
- The uniformity requirement is modeled as a constraint on `cache_block_size` because the text says the size of a cache block shall be uniform throughout the system.
- `cache_information_discoverability` is included as an architectural property and also referenced as a discoverability constraint on relevant cache parameters. This makes the discoverability decision explicit without inventing discovery mechanism details.

CSR snippet decisions:

- `csr_address_width` captures the 12-bit CSR address encoding space.
- `csr_encoding_space_capacity` captures "up to 4,096 CSRs" as an encoding-space capacity limit. It is related to address width but is not double-counted as another field-width parameter.
- `csr_accessibility_field` captures the composite `csr[11:8]` field.
- `csr_read_write_access_field` and `csr_lowest_privilege_access_field` are included as meaningful subfields and linked to the composite field.
- The gold standard does not add privilege level value meanings because the snippet does not provide them.
