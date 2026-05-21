from datetime import datetime, timezone

from typer.testing import CliRunner

from updatemenow import __version__
from updatemenow.cli import app
from updatemenow.models import ScanResult


runner = CliRunner()


def test_version_option_prints_version() -> None:
    result = runner.invoke(app, ["--version"])

    assert result.exit_code == 0
    assert f"UpdateMeNow {__version__}" in result.stdout


def test_bare_umn_runs_scan_summary(monkeypatch) -> None:
    def fake_run_scan(request, sources, keywords):
        return ScanResult(
            scan_id="test-scan",
            started_at=datetime.now(timezone.utc),
            range_hours=request.range_hours,
            sources_requested=request.sources_requested,
            sources_scanned=3,
            raw_item_count=10,
            duplicates_removed=2,
            final_item_count=8,
            items=[],
            export_paths=["reports/UpdateMeNow_Report_2026-05-20_6h.xlsx"],
        )

    monkeypatch.setattr("updatemenow.cli.run_scan", fake_run_scan)

    result = runner.invoke(app, [])

    assert result.exit_code == 0
    assert "UpdateMeNow Cyber Update Scan" in result.stdout
    assert "Last 6 hours" in result.stdout
    assert "Sources scanned: 3" in result.stdout
    assert "Dedupe mode: normal" in result.stdout
    assert "Final items: 8" in result.stdout
    assert "Report exported:" in result.stdout
    assert "reports/UpdateMeNow_Report_2026-05-20_6h.xlsx" in result.stdout


def test_scan_rejects_hours_and_days_together() -> None:
    result = runner.invoke(app, ["scan", "--hours", "24", "--days", "7"])

    assert result.exit_code == 2
    assert "--hours and --days cannot be used together" in result.stdout


def test_scan_accepts_dedupe_mode_option(monkeypatch) -> None:
    def fake_run_scan(request, sources, keywords):
        assert request.dedupe_mode.value == "relaxed"
        return ScanResult(
            scan_id="test-scan",
            started_at=datetime.now(timezone.utc),
            range_hours=request.range_hours,
            sources_requested=request.sources_requested,
            sources_scanned=1,
            raw_item_count=1,
            duplicates_removed=0,
            final_item_count=1,
            items=[],
            export_paths=["reports/UpdateMeNow_Report_2026-05-20_6h.xlsx"],
        )

    monkeypatch.setattr("updatemenow.cli.run_scan", fake_run_scan)

    result = runner.invoke(app, ["scan", "--dedupe", "relaxed"])

    assert result.exit_code == 0
    assert "Dedupe mode: relaxed" in result.stdout
