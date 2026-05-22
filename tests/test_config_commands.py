from pathlib import Path

from typer.testing import CliRunner

from updatemenow.cli import app


runner = CliRunner()


def test_config_init_creates_default_files() -> None:
    with runner.isolated_filesystem():
        result = runner.invoke(app, ["config", "init"])

        assert result.exit_code == 0
        assert Path("config/sources.yaml").exists()
        assert Path("config/keywords.yaml").exists()
        assert "created config/sources.yaml" in result.stdout
        assert "created config/keywords.yaml" in result.stdout


def test_config_init_skips_existing_files_without_force() -> None:
    with runner.isolated_filesystem():
        config_dir = Path("config")
        config_dir.mkdir()
        sources_path = config_dir / "sources.yaml"
        sources_path.write_text("sources: []\n", encoding="utf-8")

        result = runner.invoke(app, ["config", "init"])

        assert result.exit_code == 0
        assert sources_path.read_text(encoding="utf-8") == "sources: []\n"
        assert "skipped config/sources.yaml already exists" in result.stdout


def test_config_validate_accepts_initialized_defaults() -> None:
    with runner.isolated_filesystem():
        init_result = runner.invoke(app, ["config", "init"])
        validate_result = runner.invoke(app, ["config", "validate"])

        assert init_result.exit_code == 0
        assert validate_result.exit_code == 0
        assert "Config is valid." in validate_result.stdout
        assert "Sources: 35" in validate_result.stdout
        assert "Enabled sources: 12" in validate_result.stdout


def test_config_validate_stays_strict_without_local_config() -> None:
    with runner.isolated_filesystem():
        result = runner.invoke(app, ["config", "validate"])

        assert result.exit_code == 1
        assert "Missing config file: config/sources.yaml" in result.stdout
        assert "Missing config file: config/keywords.yaml" in result.stdout


def test_config_validate_rejects_enabled_source_without_provider_or_url() -> None:
    with runner.isolated_filesystem():
        config_dir = Path("config")
        config_dir.mkdir()
        (config_dir / "sources.yaml").write_text(
            "\n".join(
                [
                    "sources:",
                    "  - id: broken",
                    "    name: Broken Source",
                    "    group: government",
                    "    type: api",
                    "    enabled: true",
                    "",
                ]
            ),
            encoding="utf-8",
        )
        (config_dir / "keywords.yaml").write_text(
            "\n".join(
                [
                    "watchlists:",
                    "  default:",
                    "    - ransomware",
                    "  vendors:",
                    "    - Microsoft",
                    "",
                ]
            ),
            encoding="utf-8",
        )

        result = runner.invoke(app, ["config", "validate"])

        assert result.exit_code == 1
        assert "enabled source 'broken' needs url or provider" in result.stdout
        assert "API source 'broken' needs provider" in result.stdout


def test_config_validate_rejects_enabled_api_source_with_unknown_provider() -> None:
    with runner.isolated_filesystem():
        config_dir = Path("config")
        config_dir.mkdir()
        (config_dir / "sources.yaml").write_text(
            "\n".join(
                [
                    "sources:",
                    "  - id: broken",
                    "    name: Broken Source",
                    "    group: government",
                    "    type: api",
                    "    provider: unknown_provider",
                    "    enabled: true",
                    "",
                ]
            ),
            encoding="utf-8",
        )
        (config_dir / "keywords.yaml").write_text(
            "\n".join(
                [
                    "watchlists:",
                    "  default:",
                    "    - ransomware",
                    "  vendors:",
                    "    - Microsoft",
                    "",
                ]
            ),
            encoding="utf-8",
        )

        result = runner.invoke(app, ["config", "validate"])

        assert result.exit_code == 1
        assert "API source 'broken' uses unknown provider" in result.stdout
        assert "unknown_provider" in result.stdout
