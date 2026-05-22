from __future__ import annotations

from pathlib import Path

from updatemenow.exporters.common import REPORTS_DIR, report_base_name
from updatemenow.exporters.excel import write_excel_report
from updatemenow.exporters.json_report import write_json_report
from updatemenow.models import ExportFormat, ScanRequest, ScanResult, SourceConfig


def export_reports(
    request: ScanRequest,
    result: ScanResult,
    sources: list[SourceConfig],
    output_dir: Path = REPORTS_DIR,
) -> ScanResult:
    output_dir.mkdir(parents=True, exist_ok=True)
    export_targets = _export_targets(request, result, output_dir)
    result_with_paths = result.model_copy(
        update={"export_paths": [str(path) for _, path in export_targets]}
    )

    for export_format, path in export_targets:
        if export_format == ExportFormat.EXCEL:
            write_excel_report(result_with_paths, path)
        elif export_format == ExportFormat.JSON:
            write_json_report(request, result_with_paths, sources, path)

    return result_with_paths


def _export_targets(
    request: ScanRequest,
    result: ScanResult,
    output_dir: Path,
) -> list[tuple[ExportFormat, Path]]:
    base_name = report_base_name(request, result)
    targets: list[tuple[ExportFormat, Path]] = []
    seen_formats: set[ExportFormat] = set()

    for export_format in request.exports:
        if export_format in seen_formats:
            continue
        seen_formats.add(export_format)

        extension = "xlsx" if export_format == ExportFormat.EXCEL else "json"
        targets.append((export_format, output_dir / f"{base_name}.{extension}"))

    return targets
