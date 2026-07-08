"""Canonical slug helper shared across the SDK and kumiho-memory.

One implementation so a fix (e.g. Unicode handling) can't land in one copy
and silently miss another.
"""

from __future__ import annotations

import hashlib
import re

# ``\w`` is Unicode-aware, so letters in any script — Latin, Hangul, CJK,
# Cyrillic — are kept; only separators/punctuation collapse to a hyphen.
# kref path segments accept Unicode letters server-side, so a Korean or
# Japanese name slugs to itself instead of the empty string.
_SEP_PATTERN = re.compile(r"[^\w]+", re.UNICODE)

DEFAULT_MAX_SLUG_LEN = 48


def slugify(value: str, max_len: int = DEFAULT_MAX_SLUG_LEN, hash_on_truncate: bool = False) -> str:
    """Normalize *value* to a slug usable as a kref item/space name.

    - Casefold + Unicode-word normalization (non-ASCII letters preserved).
    - When ``hash_on_truncate`` is set and the normalized form exceeds
      ``max_len``, a short hash of the *full* normalized string is appended
      so two distinct long names sharing a prefix keep distinct slugs
      (identity safety — a wrong merge is unrecoverable). Callers that use
      the slug only for display leave it off.
    """
    base = _SEP_PATTERN.sub("-", value.casefold().strip()).strip("-")
    if not base:
        return ""
    if len(base) <= max_len:
        return base
    if hash_on_truncate:
        digest = hashlib.sha1(base.encode("utf-8")).hexdigest()[:8]
        head = base[: max_len - 9].rstrip("-")
        return f"{head}-{digest}"
    return base[:max_len].strip("-")
