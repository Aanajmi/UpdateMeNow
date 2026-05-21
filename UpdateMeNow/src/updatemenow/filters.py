from __future__ import annotations

from datetime import datetime, timedelta, timezone

from updatemenow.models import CyberUpdateItem, ScanRequest


def filter_by_time(
    items: list[CyberUpdateItem],
    request: ScanRequest,
    now: datetime | None = None,
) -> list[CyberUpdateItem]:
    current_time = now or datetime.now(timezone.utc)
    start_time = current_time - timedelta(hours=request.range_hours)

    return [
        item
        for item in items
        if item.published_at is not None and _as_utc(item.published_at) >= start_time
    ]


def filter_by_keywords(
    items: list[CyberUpdateItem],
    request: ScanRequest,
) -> list[CyberUpdateItem]:
    if not request.keywords:
        return items

    requested_keywords = {keyword.casefold() for keyword in request.keywords}
    return [
        item
        for item in items
        if requested_keywords.intersection(keyword.casefold() for keyword in item.keywords_matched)
    ]


def _as_utc(value: datetime) -> datetime:
    if value.tzinfo is None:
        return value.replace(tzinfo=timezone.utc)
    return value.astimezone(timezone.utc)
