from __future__ import annotations

import re
import unicodedata


def normalize_whitespace(value: str) -> str:
    return " ".join(value.split())


def normalize_unicode_dashes(value: str) -> str:
    return value.replace("–", "-").replace("—", "-").replace("−", "-")


def normalize_name(value: str) -> str:
    text = unicodedata.normalize("NFKD", normalize_unicode_dashes(value)).encode("ascii", "ignore")
    lowered = text.decode("ascii").lower()
    lowered = re.sub(r"[^a-z0-9]+", "_", lowered)
    return re.sub(r"_+", "_", lowered).strip("_")


BIT_RANGE_RE = re.compile(
    r"^(?:(?P<field>[A-Za-z_][A-Za-z0-9_]*)\s*)?"
    r"\[(?P<hi>\d+)(?::(?P<lo>\d+))?\]$"
)


def normalize_bit_range(value: str) -> str:
    compact = value.strip().replace(" ", "")
    if "[" not in compact and re.match(r"^[A-Za-z_][A-Za-z0-9_]*\d+:\d+$", compact):
        prefix = re.sub(r"\d.*", "", compact)
        digits = compact[len(prefix) :]
        compact = f"{prefix}[{digits}]"
    match = BIT_RANGE_RE.match(compact)
    if not match:
        raise ValueError(f"invalid bit range syntax: {value}")
    hi = int(match.group("hi"))
    lo = int(match.group("lo") or match.group("hi"))
    if hi < lo:
        raise ValueError(f"bit range high bit is smaller than low bit: {value}")
    field = match.group("field") or ""
    return f"{field}[{hi}:{lo}]" if hi != lo else f"{field}[{hi}]"
