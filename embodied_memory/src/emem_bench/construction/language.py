"""English-only validation for generated benchmark JSON."""

from __future__ import annotations

import re
from typing import Any


HAN_RE = re.compile("[\u3400-\u4dbf\u4e00-\u9fff\uf900-\ufaff\U00020000-\U000323af]")


def validate_english_payload(value: Any, path: str = "$") -> None:
    """Reject Chinese anywhere in decoded JSON, including nested object keys."""
    if isinstance(value, dict):
        for key, child in value.items():
            if isinstance(key, str) and HAN_RE.search(key):
                raise ValueError(f"Chinese object key at {path}: use an English key")
            validate_english_payload(child, f"{path}.{key}")
    elif isinstance(value, (list, tuple)):
        for index, child in enumerate(value):
            validate_english_payload(child, f"{path}[{index}]")
    elif isinstance(value, str) and HAN_RE.search(value):
        raise ValueError(
            f"Chinese text at {path}: translate it to English before saving"
        )
