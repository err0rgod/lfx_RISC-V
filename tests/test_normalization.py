from __future__ import annotations

import pytest

from riscv_parameter_extractor.normalization import (
    normalize_bit_range,
    normalize_name,
    normalize_unicode_dashes,
    normalize_whitespace,
)


def test_name_normalization() -> None:
    assert normalize_name("CSR Address Width") == "csr_address_width"
    assert normalize_name("cache-block size") == "cache_block_size"


def test_whitespace_normalization() -> None:
    assert normalize_whitespace("a\n  b\tc") == "a b c"


def test_unicode_dash_normalization() -> None:
    assert normalize_unicode_dashes("read–write") == "read-write"


def test_bitfield_normalization() -> None:
    assert normalize_bit_range("csr[11:8]") == "csr[11:8]"
    assert normalize_bit_range("[9:8]") == "[9:8]"


def test_invalid_bitfield_rejected() -> None:
    with pytest.raises(ValueError):
        normalize_bit_range("csr[8:11]")
