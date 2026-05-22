from __future__ import annotations

import hashlib
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from typing import Any


def stable_item_id(source_id: str, value: str) -> str:
    digest = hashlib.sha256(f"{source_id}:{value}".encode("utf-8")).hexdigest()[:16]
    return f"{source_id}:{digest}"


def parse_datetime(value: Any) -> datetime | None:
    if value is None:
        return None

    if isinstance(value, datetime):
        parsed = value
    elif isinstance(value, str):
        parsed = _parse_datetime_string(value)
    else:
        return None

    if parsed.tzinfo is None:
        return parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


def parse_date(value: str | None) -> datetime | None:
    if not value:
        return None
    parsed = _parse_datetime_string(f"{value}T00:00:00Z")
    return parsed.astimezone(timezone.utc)


def _parse_datetime_string(value: str) -> datetime:
    normalized = value.strip()
    if normalized.endswith("Z"):
        normalized = f"{normalized[:-1]}+00:00"

    try:
        return datetime.fromisoformat(normalized)
    except ValueError:
        parsed = parsedate_to_datetime(value)
        return parsed


def truncate_text(value: str, max_length: int = 140) -> str:
    clean_value = " ".join(value.split())
    if len(clean_value) <= max_length:
        return clean_value
    return f"{clean_value[: max_length - 3].rstrip()}..."
