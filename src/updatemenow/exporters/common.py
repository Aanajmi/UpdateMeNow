from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from updatemenow.models import CyberUpdateItem, ScanRequest, ScanResult, SourceConfig

REPORTS_DIR = Path("reports")
REPORT_COLUMNS = [
    "Source Group",
    "Source Name",
    "Source Type",
    "Published Date",
    "Age",
    "Title",
    "Description",
    "URL",
    "CVEs",
    "Keywords Matched",
    "Vendors/Products Matched",
    "Category",
    "Scan Run Time",
]


def report_base_name(request: ScanRequest, result: ScanResult) -> str:
    report_date = _as_utc(result.started_at).strftime("%Y-%m-%d")
    return f"UpdateMeNow_Report_{report_date}_{range_suffix(request)}"


def range_suffix(request: ScanRequest) -> str:
    if request.days is not None:
        return f"{request.days}d"
    return f"{request.hours or 6}h"


def item_to_report_row(item: CyberUpdateItem, reference_time: datetime) -> list[str]:
    return [
        item.source_group,
        item.source_name,
        item.source_type.value,
        format_datetime(item.published_at),
        format_age(item.published_at, reference_time),
        item.title,
        item.description,
        item.url,
        ", ".join(item.cves),
        ", ".join(item.keywords_matched),
        ", ".join(item.vendors_matched),
        item.category,
        format_datetime(item.scan_run_time),
    ]


def item_to_json(item: CyberUpdateItem, reference_time: datetime) -> dict[str, Any]:
    return {
        "id": item.id,
        "source_id": item.source_id,
        "source_name": item.source_name,
        "source_group": item.source_group,
        "source_type": item.source_type.value,
        "published_at": format_datetime(item.published_at),
        "age": format_age(item.published_at, reference_time),
        "title": item.title,
        "description": item.description,
        "url": item.url,
        "cves": item.cves,
        "keywords_matched": item.keywords_matched,
        "vendors_matched": item.vendors_matched,
        "category": item.category,
        "scan_run_time": format_datetime(item.scan_run_time),
    }


def source_to_json(source: SourceConfig) -> dict[str, Any]:
    return {
        "id": source.id,
        "name": source.name,
        "group": source.group,
        "type": source.type.value,
        "url": source.url,
        "provider": source.provider,
        "enabled": source.enabled,
        "default_order": source.default_order,
    }


def format_datetime(value: datetime | None) -> str:
    if value is None:
        return ""
    return _as_utc(value).isoformat().replace("+00:00", "Z")


def format_age(published_at: datetime | None, reference_time: datetime) -> str:
    if published_at is None:
        return "unknown"

    delta = _as_utc(reference_time) - _as_utc(published_at)
    total_seconds = max(0, int(delta.total_seconds()))
    if total_seconds < 3600:
        minutes = total_seconds // 60
        return f"{minutes}m ago"
    if total_seconds < 86400:
        hours = total_seconds // 3600
        return f"{hours}h ago"
    days = total_seconds // 86400
    return f"{days}d ago"


def _as_utc(value: datetime) -> datetime:
    if value.tzinfo is None:
        return value.replace(tzinfo=timezone.utc)
    return value.astimezone(timezone.utc)
