from typer.testing import CliRunner

from updatemenow.cli import app
from updatemenow.models import SourceType
from updatemenow.sources.health import SourceCheckResult


runner = CliRunner()


def test_sources_list_shows_configured_sources() -> None:
    result = runner.invoke(app, ["sources", "list"])

    assert result.exit_code == 0
    assert "UpdateMeNow Sources" in result.stdout
    assert "cisa_kev" in result.stdout
    assert "cisa_alerts" in result.stdout
    assert "nvd" in result.stdout
    assert "github" in result.stdout


def test_sources_list_uses_packaged_defaults_without_local_config() -> None:
    with runner.isolated_filesystem():
        result = runner.invoke(app, ["sources", "list"])

    assert result.exit_code == 0
    assert "UpdateMeNow Sources" in result.stdout
    assert "cisa_kev" in result.stdout
    assert "nvd" in result.stdout


def test_sources_test_reports_success(monkeypatch) -> None:
    def fake_check_source_catalog(catalog, timeout, include_disabled=False):
        assert include_disabled is False
        return [
            SourceCheckResult(
                source_id="nvd",
                source_type=SourceType.API,
                endpoint="https://services.nvd.nist.gov/rest/json/cves/2.0",
                ok=True,
                message="Reachable.",
                status_code=200,
            )
        ]

    monkeypatch.setattr("updatemenow.cli.check_source_catalog", fake_check_source_catalog)

    result = runner.invoke(app, ["sources", "test"])

    assert result.exit_code == 0
    assert "UpdateMeNow Source Reachability" in result.stdout
    assert "nvd" in result.stdout
    assert "Reachable." in result.stdout


def test_sources_test_exits_nonzero_on_failure(monkeypatch) -> None:
    def fake_check_source_catalog(catalog, timeout, include_disabled=False):
        return [
            SourceCheckResult(
                source_id="broken",
                source_type=SourceType.API,
                endpoint="https://example.invalid/api",
                ok=False,
                message="Name or service not known",
            )
        ]

    monkeypatch.setattr("updatemenow.cli.check_source_catalog", fake_check_source_catalog)

    result = runner.invoke(app, ["sources", "test"])

    assert result.exit_code == 1
    assert "failed" in result.stdout
    assert "known" in result.stdout


def test_sources_test_all_checks_disabled_sources(monkeypatch) -> None:
    def fake_check_source_catalog(catalog, timeout, include_disabled=False):
        assert include_disabled is True
        return [
            SourceCheckResult(
                source_id="exploit_db",
                source_type=SourceType.RSS,
                endpoint="https://www.exploit-db.com/rss.xml",
                ok=True,
                message="Reachable.",
                status_code=200,
            )
        ]

    monkeypatch.setattr("updatemenow.cli.check_source_catalog", fake_check_source_catalog)

    result = runner.invoke(app, ["sources", "test", "--all"])

    assert result.exit_code == 0
    assert "All Sources" in result.stdout
    assert "exploit_db" in result.stdout
