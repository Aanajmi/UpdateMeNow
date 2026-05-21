from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from updatemenow.exporters.common import format_datetime, item_to_json, range_suffix, source_to_json
from updatemenow.models import ScanRequest, ScanResult, SourceConfig


def write_json_report(
    request: ScanRequest,
    result: ScanResult,
    sources: list[SourceConfig],
    path: Path,
) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(
            _json_payload(request, result, sources),
            indent=2,
            ensure_ascii=False,
        )
        + "\n",
        encoding="utf-8",
    )


def _json_payload(
    request: ScanRequest,
    result: ScanResult,
    sources: list[SourceConfig],
) -> dict[str, Any]:
    return {
        "scan": {
            "scan_id": result.scan_id,
            "run_time": format_datetime(result.started_at),
            "started_at": format_datetime(result.started_at),
            "ended_at": format_datetime(result.ended_at),
            "range": range_suffix(request),
            "range_hours": result.range_hours,
            "sources_requested": result.sources_requested,
            "sources_scanned": result.sources_scanned,
            "raw_items": result.raw_item_count,
            "duplicates_removed": result.duplicates_removed,
            "dedupe_mode": request.dedupe_mode.value,
            "final_items": result.final_item_count,
            "exports": [export.value for export in request.exports],
            "export_paths": result.export_paths,
        },
        "sources": [source_to_json(source) for source in sources],
        "items": [item_to_json(item, result.started_at) for item in result.items],
    }
